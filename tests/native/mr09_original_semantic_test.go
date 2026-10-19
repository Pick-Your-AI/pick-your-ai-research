package gguf_parser

import (
	"encoding/json"
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

// This exact test is first executed on the unchanged pinned upstream source.
// Its failure is the targeted semantic reproduction, not a physical accuracy test.
func TestMR09OriginalSemanticFixture(t *testing.T) {
	f := mr09SyntheticFile()
	e := f.EstimateLLaMACppRun(mr09BaselineOptions(512, 256, 1)...)
	const bootstrap = 5*1024*1024 + 1024
	if got := uint64(e.Devices[0].Footprint) - bootstrap; got != 64 {
		t.Errorf("initial host output payload: got %d bytes; one 16-float logits row requires 64", got)
	}
	if got := uint64(e.Devices[1].Computation.Output); got != 24576 {
		t.Errorf("device output graph term: got %d bytes; 256 rows of 8-float normalization and 16-float logits require 24576", got)
	}
	if got := uint64(e.Devices[0].Computation.Output); got != 0 {
		t.Errorf("output graph placed on host: got %d bytes; full-offloaded output weight belongs to the device", got)
	}
}

// A machine-readable baseline supports exact default-behavior preservation.
func TestMR09DefaultBehaviorReceipt(t *testing.T) {
	for _, controls := range [][3]int32{{512, 256, 1}, {256, 128, 1}, {1024, 256, 1}, {512, 256, 2}} {
		e := mr09SyntheticFile().EstimateLLaMACppRun(mr09BaselineOptions(controls[0], controls[1], controls[2])...)
		b, err := json.Marshal(e)
		if err != nil { t.Fatal(err) }
		t.Logf("DEFAULT %v %s", controls, b)
	}
}
