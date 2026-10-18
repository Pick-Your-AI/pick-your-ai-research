// Initialization-only qualification harness. No decode/encode API is loaded.
// Uses the pinned external llama.cpp headers/DLLs; no third-party source copied.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "llama.h"
#include "ggml-backend-impl.h"
#include "mr09_quota.hpp"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>

static mr09_quota * quota = nullptr;
static ggml_backend_buffer_t (*original_alloc)(ggml_backend_buffer_type_t,size_t) = nullptr;
static ggml_backend_t (*original_init)(ggml_backend_dev_t,const char *) = nullptr;
static std::mutex records_mutex;
struct allocation { size_t size; void (*free_fn)(ggml_backend_buffer_t); };
static std::map<ggml_backend_buffer_t, allocation> records;
static size_t native_allocator_calls = 0, graph_denials = 0;

static void capped_free(ggml_backend_buffer_t buffer) {
    allocation item;
    {
        std::lock_guard<std::mutex> lock(records_mutex);
        auto it = records.find(buffer);
        if (it == records.end()) std::abort();
        item = it->second;
        records.erase(it);
    }
    // The outer ggml API frees the buffer descriptor after this callback.
    if (item.free_fn) item.free_fn(buffer);
    quota->release(item.size);
}
static ggml_backend_buffer_t capped_alloc(ggml_backend_buffer_type_t buft,size_t size) {
    // Reserve before forwarding, including simultaneous/in-flight requests.
    if (!quota->reserve(size)) return nullptr;
    { std::lock_guard<std::mutex> lock(records_mutex); ++native_allocator_calls; }
    auto buffer = original_alloc(buft,size);
    if (!buffer) { quota->release(size); return nullptr; }
    // Pinned CUDA allocator forwards this size unchanged to its device allocator.
    if (buffer->size != size) std::abort();
    {
        std::lock_guard<std::mutex> lock(records_mutex);
        if (!records.emplace(buffer,allocation{size,buffer->iface.free_buffer}).second) std::abort();
        buffer->iface.free_buffer = capped_free;
    }
    return buffer;
}
static ggml_status forbid_graph(ggml_backend_t,ggml_cgraph *) {
    ++graph_denials;
    return GGML_STATUS_FAILED;
}
static ggml_status forbid_plan(ggml_backend_t,ggml_backend_graph_plan_t) {
    ++graph_denials;
    return GGML_STATUS_FAILED;
}
static ggml_backend_t guarded_init(ggml_backend_dev_t dev,const char * params) {
    auto backend = original_init(dev,params);
    if (!backend) return nullptr;
    backend->iface.graph_compute = forbid_graph;
    backend->iface.graph_plan_compute = forbid_plan;
    return backend;
}
template<class F> static F symbol(HMODULE module,const char * name) {
    auto result = GetProcAddress(module,name);
    if (!result) throw std::runtime_error(std::string("missing export: ")+name);
    return reinterpret_cast<F>(result);
}
static HMODULE load(const std::string & dir,const char * name) {
    char absolute[32768];
    if (!GetFullPathNameA((dir+"/"+name).c_str(),sizeof(absolute),absolute,nullptr)) throw std::runtime_error("path normalization failed");
    auto module = LoadLibraryExA(absolute,nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    if (!module) throw std::runtime_error(std::string("DLL load failed: ")+name+" Win32="+std::to_string(GetLastError()));
    return module;
}
static void cap_record(const char * stage) {
    auto s=quota->snapshot();
    std::printf("{\"mr09_event\":\"cap\",\"stage\":\"%s\",\"cap_bytes\":%llu,\"live_bytes\":%llu,\"peak_admitted_bytes\":%llu,\"admission_denials\":%llu,\"native_allocator_calls\":%llu,\"graph_denials\":%llu}\n",
        stage,(unsigned long long)s.limit,(unsigned long long)s.current,(unsigned long long)s.peak,
        (unsigned long long)s.denied,(unsigned long long)native_allocator_calls,(unsigned long long)graph_denials);
    std::fflush(stdout);
}
int main(int argc,char **argv) {
    try {
        if(argc<3 || argc>4) throw std::runtime_error("usage: native-init runtime-dir cap-bytes [pinned-model.gguf]");
        char * end=nullptr;
        auto cap=std::strtoull(argv[2],&end,10);
        if(!end || *end || !cap || cap>2136809472ULL) throw std::runtime_error("invalid or expanded cap");
        // Only this child process is affected. Remove environment changes on exit.
        SetEnvironmentVariableA("GGML_CUDA_DISABLE_GRAPHS","1");
        SetEnvironmentVariableA("GGML_CUDA_ENABLE_UNIFIED_MEMORY",nullptr);
        SetEnvironmentVariableA("GGML_CUDA_DEVICES",nullptr);
        SetEnvironmentVariableA("GGML_CUDA_P2P",nullptr);
        auto dir=std::string(argv[1]);
        auto base=load(dir,"ggml-base.dll");
        auto registry=load(dir,"ggml.dll");
        auto runtime=load(dir,"llama.dll");
        auto common=load(dir,"llama-common.dll");
        auto load_backend=symbol<decltype(&ggml_backend_load)>(registry,"ggml_backend_load");
        if(!load_backend((dir+"/ggml-cpu-x64.dll").c_str())) throw std::runtime_error("CPU backend unavailable");
        if(!load_backend((dir+"/ggml-cuda.dll").c_str())) throw std::runtime_error("CUDA backend unavailable");
        auto device=symbol<decltype(&ggml_backend_dev_by_name)>(registry,"ggml_backend_dev_by_name")("CUDA0");
        if(!device) throw std::runtime_error("CUDA0 unavailable; no CPU fallback");
        auto buft=symbol<decltype(&ggml_backend_dev_buffer_type)>(base,"ggml_backend_dev_buffer_type")(device);
        auto name=symbol<decltype(&ggml_backend_buft_name)>(base,"ggml_backend_buft_name");
        if(std::strcmp(name(buft),"CUDA0") || buft->iface.alloc_buffer_n) throw std::runtime_error("unexpected CUDA buffer interface");
        size_t free=0,total=0;
        symbol<decltype(&ggml_backend_dev_memory)>(base,"ggml_backend_dev_memory")(device,&free,&total);
        if(free<4ULL*1024*1024*1024 || !total) throw std::runtime_error("CUDA discovery guard failed");
        cap=std::min<unsigned long long>(cap,total/8);
        mr09_quota budget(static_cast<size_t>(cap)); quota=&budget;
        original_alloc=buft->iface.alloc_buffer;
        original_init=device->iface.init_backend;
        buft->iface.alloc_buffer=capped_alloc;
        device->iface.init_backend=guarded_init;
        auto allocate=symbol<decltype(&ggml_backend_buft_alloc_buffer)>(base,"ggml_backend_buft_alloc_buffer");
        auto release=symbol<decltype(&ggml_backend_buffer_free)>(base,"ggml_backend_buffer_free");
        auto clear=symbol<decltype(&ggml_backend_buffer_clear)>(base,"ggml_backend_buffer_clear");
        auto probe=allocate(buft,8*1024*1024);
        if(!probe) throw std::runtime_error("8 MiB allocation probe failed");
        clear(probe,0); // Native CUDA clear/synchronize checks an actual operation.
        auto calls=native_allocator_calls;
        if(allocate(buft,static_cast<size_t>(cap)+1) || native_allocator_calls!=calls) throw std::runtime_error("over-cap request forwarded");
        release(probe);
        auto backend=guarded_init(device,nullptr);
        if(!backend || backend->iface.graph_compute(backend,nullptr)!=GGML_STATUS_FAILED) throw std::runtime_error("graph execution guard failed");
        symbol<decltype(&ggml_backend_free)>(base,"ggml_backend_free")(backend);
        if(budget.snapshot().current!=0) throw std::runtime_error("probe memory not released");
        std::printf("{\"mr09_event\":\"qualification\",\"status\":\"probe_passed\",\"device\":\"CUDA0\",\"driver_total_bytes\":%llu,\"cuda_reported_free_bytes\":%llu,\"graphs_disabled\":true,\"decode_api_loaded\":false}\n",(unsigned long long)total,(unsigned long long)free);
        cap_record("after_probe");
        if(argc==4) {
            auto model_params=symbol<decltype(&llama_model_default_params)>(runtime,"llama_model_default_params")();
            ggml_backend_dev_t devices[]={device,nullptr};
            model_params.devices=devices;
            model_params.n_gpu_layers=31;
            model_params.split_mode=LLAMA_SPLIT_MODE_NONE;
            model_params.main_gpu=0;
            model_params.load_mode=LLAMA_LOAD_MODE_MMAP;
            model_params.no_alloc=false;
            model_params.vocab_only=false;
            model_params.use_extra_bufts=false; // No repack/alternate allocator can bypass the boundary.
            auto load_model=symbol<decltype(&llama_model_load_from_file)>(runtime,"llama_model_load_from_file");
            auto model=load_model(argv[3],model_params);
            if(!model) throw std::runtime_error("native model load failed");
            auto context_params=symbol<decltype(&llama_context_default_params)>(runtime,"llama_context_default_params")();
            context_params.n_ctx=512;context_params.n_batch=256;context_params.n_ubatch=256;
            context_params.n_seq_max=1;context_params.n_threads=4;context_params.n_threads_batch=4;
            context_params.type_k=GGML_TYPE_F16;context_params.type_v=GGML_TYPE_F16;
            context_params.flash_attn_type=LLAMA_FLASH_ATTN_TYPE_DISABLED;
            context_params.offload_kqv=true;context_params.op_offload=true;
            auto context=symbol<decltype(&llama_init_from_model)>(runtime,"llama_init_from_model")(model,context_params);
            if(!context) throw std::runtime_error("native context initialization failed");
            auto nctx=symbol<decltype(&llama_n_ctx)>(runtime,"llama_n_ctx")(context);
            auto nb=symbol<decltype(&llama_n_batch)>(runtime,"llama_n_batch")(context);
            auto nub=symbol<decltype(&llama_n_ubatch)>(runtime,"llama_n_ubatch")(context);
            auto ns=symbol<decltype(&llama_n_seq_max)>(runtime,"llama_n_seq_max")(context);
            if(nctx!=512 || nb!=256 || nub!=256 || ns!=1 || graph_denials!=1) throw std::runtime_error("effective config/execution drift");
            symbol<decltype(&llama_synchronize)>(runtime,"llama_synchronize")(context);
            std::puts("{\"mr09_event\":\"effective\",\"no_alloc\":false,\"context\":512,\"batch\":256,\"ubatch\":256,\"sequences\":1,\"generation_forwards\":0,\"warmup\":false,\"extra_buffer_types\":false}");
            cap_record("before_capture");
            symbol<void(*)(bool)>(common,"?common_log_set_jsonl@@YAX_N@Z")(true);
            symbol<void(*)(const llama_context*)>(common,"?common_memory_breakdown_print@@YAXPEBUllama_context@@@Z")(context);
            auto logger=symbol<void*(*)()>(common,"?common_log_main@@YAPEAUcommon_log@@XZ")();
            symbol<void(*)(void*)>(common,"?common_log_flush@@YAXPEAUcommon_log@@@Z")(logger);
            symbol<decltype(&llama_free)>(runtime,"llama_free")(context);
            symbol<decltype(&llama_model_free)>(runtime,"llama_model_free")(model);
            if(budget.snapshot().current || !records.empty()) throw std::runtime_error("managed allocations remain after cleanup");
            cap_record("after_cleanup");
            std::puts("{\"mr09_event\":\"result\",\"status\":\"initialization_qualified\",\"scope\":\"initialization-only managed buffers; not process-wide peak or inference\"}");
        }
        buft->iface.alloc_buffer=original_alloc;
        device->iface.init_backend=original_init;
        return 0;
    } catch(const std::exception &e) {
        std::fprintf(stderr,"qualification failed: %s\n",e.what());
        return 1;
    }
}
