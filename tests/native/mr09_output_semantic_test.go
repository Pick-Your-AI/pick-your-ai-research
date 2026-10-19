package gguf_parser

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"sort"
	"testing"
)

// The fixture is synthetic metadata only. It is not an observed model or GPU run.
func mr09SyntheticFile() *GGUFFile {
	kv := []GGUFMetadataKV{
		{Key: "general.architecture", ValueType: GGUFMetadataValueTypeString, Value: "llama"},
	}
	for key, value := range map[string]uint32{
		"context_length": 2048, "embedding_length": 8, "block_count": 1,
		"feed_forward_length": 16, "attention.head_count": 2,
		"attention.head_count_kv": 1, "attention.key_length": 4,
		"attention.value_length": 4, "vocab_size": 16,
	} {
		kv = append(kv, GGUFMetadataKV{Key: "llama." + key, ValueType: GGUFMetadataValueTypeUint32, Value: value})
	}
	tensors := GGUFTensorInfos{}
	for _, item := range []struct {
		name string
		dims []uint64
	}{
		{"token_embd.weight", []uint64{8, 16}},
		{"blk.0.attn_norm.weight", []uint64{8}},
		{"blk.0.attn_q.weight", []uint64{8, 8}},
		{"blk.0.attn_k.weight", []uint64{8, 4}},
		{"blk.0.attn_v.weight", []uint64{8, 4}},
		{"blk.0.attn_output.weight", []uint64{8, 8}},
		{"blk.0.ffn_norm.weight", []uint64{8}},
		{"blk.0.ffn_gate.weight", []uint64{8, 16}},
		{"blk.0.ffn_up.weight", []uint64{8, 16}},
		{"blk.0.ffn_down.weight", []uint64{16, 8}},
		{"output_norm.weight", []uint64{8}},
		{"output.weight", []uint64{8, 16}},
	} {
		tensors = append(tensors, GGUFTensorInfo{Name: item.name, NDimensions: uint32(len(item.dims)), Dimensions: item.dims, Type: GGMLTypeF16})
	}
	f := &GGUFFile{Header: GGUFHeader{Version: GGUFVersionV3, MetadataKV: kv}, TensorInfos: tensors}
	f.Header.TensorCount = uint64(len(tensors))
	f.Header.MetadataKVCount = uint64(len(kv))
	for _, tensor := range tensors {
		f.ModelSize += GGUFBytesScalar(tensor.Bytes())
	}
	f.Size = f.ModelSize + 1024
	return f
}

func mr09BaselineOptions(context, batch, sequences int32) []GGUFRunEstimateOption {
	return []GGUFRunEstimateOption{
		WithLLaMACppContextSize(context),
		WithLLaMACppLogicalBatchSize(batch),
		WithLLaMACppPhysicalBatchSize(batch),
		WithParallelSize(sequences),
		WithLLaMACppOffloadLayers(2),
		WithLLaMACppSplitMode(LLaMACppSplitModeNone),
	}
}

func mr09Profile(ctx, batch, seq uint32) MR09InitBufferProfile {
	return MR09InitBufferProfile{
		RuntimeCommit: "620d2225cc436ab0b001e3200e590e3b286ef9ab", Stage: "completed-initialization-before-free",
		Allocation: "allocated", Placement: "single-CUDA0-all-layers", OutputBackend: "CUDA0", HostReadback: "host",
		Embeddings: "disabled", BackendSamplers: "disabled", FlashAttention: "disabled", MMap: "enabled",
		KVOffload: "enabled", OperationOffload: "enabled", CacheKey: "f16", CacheValue: "f16",
		ContextSize: ctx, LogicalBatchSize: batch, PhysicalBatchSize: batch, SequenceCapacity: seq,
		OutputsMax: batch, OutputsMaxPerSequence: 1,
	}
}

// Serialize a tiny, complete synthetic file. Zero payload is deliberately not a
// trained model. Tests pass its actual bytes through the pinned GGUF parser.
func mr09GGUF(t *testing.T, f *GGUFFile) []byte {
	t.Helper()
	var b bytes.Buffer
	put := func(v any) {
		if err := binary.Write(&b, binary.LittleEndian, v); err != nil {
			t.Fatal(err)
		}
	}
	str := func(s string) { put(uint64(len(s))); b.WriteString(s) }
	put(uint32(GGUFMagicGGUFLe))
	put(uint32(3))
	put(uint64(len(f.TensorInfos)))
	put(uint64(len(f.Header.MetadataKV)))
	sort.SliceStable(f.Header.MetadataKV, func(i, j int) bool { return f.Header.MetadataKV[i].Key < f.Header.MetadataKV[j].Key })
	for _, kv := range f.Header.MetadataKV {
		str(kv.Key)
		put(uint32(kv.ValueType))
		if kv.ValueType == GGUFMetadataValueTypeString {
			str(kv.Value.(string))
		} else {
			put(kv.Value)
		}
	}
	var offset uint64
	for _, tensor := range f.TensorInfos {
		str(tensor.Name)
		put(tensor.NDimensions)
		for _, d := range tensor.Dimensions {
			put(d)
		}
		put(uint32(tensor.Type))
		put(offset + tensor.Offset)
		offset = (offset + tensor.Bytes() + 31) / 32 * 32
	}
	for b.Len()%32 != 0 {
		b.WriteByte(0)
	}
	b.Write(make([]byte, offset))
	return b.Bytes()
}
func mr09Digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

func TestMR09DefaultBehaviorPreserved(t *testing.T) {
	cases := []struct {
		controls [3]int32
		hash     string
	}{
		{[3]int32{512, 256, 1}, "acb1b3c6f23d3b0bb1e8f6f8c50b25f797d6f16ad79cd4aa00a369ffd2c916d3"},
		{[3]int32{256, 128, 1}, "54457ccf079bc44e14e3743f3f64f5c28c7f0544492ebe25cff738d003213772"},
		{[3]int32{1024, 256, 1}, "f9cec7d47a6207bf43efce04ee321e32b2e85a3171c7982e8f7a79d7cbe0a70e"},
		{[3]int32{512, 256, 2}, "acb1b3c6f23d3b0bb1e8f6f8c50b25f797d6f16ad79cd4aa00a369ffd2c916d3"},
	}
	for _, c := range cases {
		t.Run(fmt.Sprint(c.controls), func(t *testing.T) {
			e := mr09SyntheticFile().EstimateLLaMACppRun(mr09BaselineOptions(c.controls[0], c.controls[1], c.controls[2])...)
			b, err := json.Marshal(e)
			if err != nil {
				t.Fatal(err)
			}
			// Hashes cover complete serialized original estimates, captured before edits.
			if got := mr09Digest(b); got != c.hash {
				t.Fatalf("default estimate changed: %s", b)
			}
		})
	}
}

func TestMR09BoundArtifactOutputSemantics(t *testing.T) {
	for _, c := range [][3]uint32{{512, 256, 1}, {256, 128, 1}, {1024, 256, 1}, {512, 256, 2}} {
		t.Run(fmt.Sprint(c), func(t *testing.T) {
			data := mr09GGUF(t, mr09SyntheticFile())
			p := mr09Profile(c[0], c[1], c[2])
			got, err := EstimateMR09InitBuffers(data, mr09Digest(data), p)
			if err != nil {
				t.Fatal(err)
			}
			parsed, err := parseGGUFFile([]_GGUFFileReadSeeker{{ReadSeeker: bytes.NewReader(data), Size: int64(len(data))}}, _GGUFReadOptions{})
			if err != nil {
				t.Fatal(err)
			}
			host := uint64(got.Estimate.Devices[0].Footprint) - 5*1024*1024 - uint64(parsed.Size-parsed.ModelSize)
			if host != uint64(c[2])*64 {
				t.Errorf("host initialization logits: got %d", host)
			}
			if got.HostReadbackRows != c[2] || got.GraphOutputRows != c[1] || got.PerSequenceContext != c[0]/c[2] {
				t.Errorf("capacity identities drifted: %+v", got)
			}
			if actual := uint64(got.Estimate.Devices[1].Computation.Output); actual != uint64(c[1])*96 {
				t.Errorf("device graph output: got %d", actual)
			}
			if got.Estimate.Devices[0].Computation.Output != 0 {
				t.Error("graph projection placed on host")
			}
			if got.ArtifactSHA256 != mr09Digest(data) || got.ArtifactBytes != uint64(len(data)) {
				t.Error("artifact binding lost")
			}
			if got.DeclaredPopulatedCache != 0 || got.DeclaredActiveRequests != 0 || got.DeclaredGeneratedTokens != 0 {
				t.Error("initialization declarations drifted")
			}
		})
	}
}

func TestMR09GlobalOutputCapacity(t *testing.T) {
	data := mr09GGUF(t, mr09SyntheticFile())
	p := mr09Profile(512, 256, 2)
	p.OutputsMax = 64
	got, err := EstimateMR09InitBuffers(data, mr09Digest(data), p)
	if err != nil {
		t.Fatal(err)
	}
	if got.GraphOutputRows != 64 || got.HostReadbackRows != 2 || got.Estimate.Devices[1].Computation.Output != 6144 {
		t.Fatalf("global output maximum was replaced by per-sequence maximum: %+v", got)
	}
	p.PhysicalBatchSize = 32
	got, err = EstimateMR09InitBuffers(data, mr09Digest(data), p)
	if err != nil {
		t.Fatal(err)
	}
	if got.GraphOutputRows != 32 || got.Estimate.Devices[1].Computation.Output != 3072 {
		t.Fatal("physical microbatch bound lost")
	}
}

func TestMR09UnsupportedControls(t *testing.T) {
	data := mr09GGUF(t, mr09SyntheticFile())
	for name, change := range map[string]func(*MR09InitBufferProfile){
		"runtime":                 func(p *MR09InitBufferProfile) { p.RuntimeCommit = "other" },
		"missing-stage":           func(p *MR09InitBufferProfile) { p.Stage = "" },
		"no-alloc":                func(p *MR09InitBufferProfile) { p.Allocation = "no_alloc" },
		"partial-offload":         func(p *MR09InitBufferProfile) { p.Placement = "partial" },
		"cpu-output":              func(p *MR09InitBufferProfile) { p.OutputBackend = "CPU" },
		"embeddings":              func(p *MR09InitBufferProfile) { p.Embeddings = "enabled" },
		"samplers":                func(p *MR09InitBufferProfile) { p.BackendSamplers = "enabled" },
		"flash":                   func(p *MR09InitBufferProfile) { p.FlashAttention = "enabled" },
		"cache":                   func(p *MR09InitBufferProfile) { p.CacheKey = "q8_0" },
		"mmap":                    func(p *MR09InitBufferProfile) { p.MMap = "disabled" },
		"kv-offload":              func(p *MR09InitBufferProfile) { p.KVOffload = "disabled" },
		"op-offload":              func(p *MR09InitBufferProfile) { p.OperationOffload = "disabled" },
		"context-overflow":        func(p *MR09InitBufferProfile) { p.ContextSize = ^uint32(0) },
		"zero-sequences":          func(p *MR09InitBufferProfile) { p.SequenceCapacity = 0 },
		"large-sequences":         func(p *MR09InitBufferProfile) { p.SequenceCapacity = 3 },
		"zero-output":             func(p *MR09InitBufferProfile) { p.OutputsMax = 0 },
		"unresolved-per-sequence": func(p *MR09InitBufferProfile) { p.OutputsMaxPerSequence = 0 },
		"physical-over-logical":   func(p *MR09InitBufferProfile) { p.PhysicalBatchSize = 257 },
	} {
		t.Run(name, func(t *testing.T) {
			p := mr09Profile(512, 256, 1)
			change(&p)
			if _, err := EstimateMR09InitBuffers(data, mr09Digest(data), p); err == nil {
				t.Fatal("unsupported controls admitted")
			}
		})
	}
}

func TestMR09RejectArtifactDrift(t *testing.T) {
	p := mr09Profile(512, 256, 1)
	data := mr09GGUF(t, mr09SyntheticFile())
	pin := mr09Digest(data)
	data[len(data)-1] ^= 1
	if _, err := EstimateMR09InitBuffers(data, pin, p); err == nil {
		t.Fatal("changed artifact admitted")
	}
	if _, err := EstimateMR09InitBuffers(data[:len(data)-128], mr09Digest(data[:len(data)-128]), p); err == nil {
		t.Fatal("truncated artifact admitted")
	}
	for name, change := range map[string]func(*GGUFFile){
		"wrong-architecture": func(f *GGUFFile) { f.Header.MetadataKV[0].Value = "mamba" },
		"duplicate-key":      func(f *GGUFFile) { f.Header.MetadataKV = append(f.Header.MetadataKV, f.Header.MetadataKV[0]) },
		"duplicate-tensor":   func(f *GGUFFile) { f.TensorInfos[1].Name = f.TensorInfos[0].Name },
		"tensor-range":       func(f *GGUFFile) { f.TensorInfos[0].Offset = 1 << 30 },
		"kv-overflow": func(f *GGUFFile) {
			for i := range f.Header.MetadataKV {
				if f.Header.MetadataKV[i].Key == "llama.attention.head_count_kv" {
					f.Header.MetadataKV[i].ValueType = GGUFMetadataValueTypeUint64
					f.Header.MetadataKV[i].Value = ^uint64(0)
				}
			}
		},
		"key-overflow": func(f *GGUFFile) {
			for i := range f.Header.MetadataKV {
				if f.Header.MetadataKV[i].Key == "llama.attention.key_length" {
					f.Header.MetadataKV[i].Value = ^uint32(0)
				}
			}
		},
		"mla": func(f *GGUFFile) {
			f.Header.MetadataKV = append(f.Header.MetadataKV, GGUFMetadataKV{Key: "llama.attention.key_length_mla", ValueType: GGUFMetadataValueTypeUint32, Value: uint32(4)})
		},
		"shape-mismatch": func(f *GGUFFile) { f.TensorInfos[1].Dimensions = []uint64{4} },
		"missing-layer":  func(f *GGUFFile) { f.TensorInfos = append(f.TensorInfos[:1], f.TensorInfos[2:]...) },
		"block-overflow": func(f *GGUFFile) {
			for i := range f.Header.MetadataKV {
				if f.Header.MetadataKV[i].Key == "llama.block_count" {
					f.Header.MetadataKV[i].Value = ^uint32(0)
				}
			}
		},
		"malformed-alignment": func(f *GGUFFile) {
			f.Header.MetadataKV = append(f.Header.MetadataKV, GGUFMetadataKV{Key: "general.alignment", ValueType: GGUFMetadataValueTypeUint32, Value: uint32(0)})
		},
	} {
		t.Run(name, func(t *testing.T) {
			f := mr09SyntheticFile()
			change(f)
			data := mr09GGUF(t, f)
			if _, err := EstimateMR09InitBuffers(data, mr09Digest(data), p); err == nil {
				t.Fatal("unsupported artifact admitted")
			}
		})
	}
}
