# Attribution and scope

This personal project was inspired by an NVIDIA livestream demonstration.
The exact broadcast URL and presenter have not yet been recorded here.
No livestream recording, slides, or presenter footage is redistributed.

## Upstream work

| Component | Owner/source | License or terms |
|---|---|---|
| Cosmos3-Edge | [NVIDIA model card](https://huggingface.co/nvidia/Cosmos3-Edge) | OpenMDW 1.1, as linked by the model card |
| TensorRT Edge-LLM | [NVIDIA repository](https://github.com/NVIDIA/TensorRT-Edge-LLM) | Apache-2.0 |
| live-vlm-webui | [NVIDIA-AI-IOT repository](https://github.com/NVIDIA-AI-IOT/live-vlm-webui) | Apache-2.0 |
| TensorRT and CUDA runtime libraries | NVIDIA packages installed separately | Their own NVIDIA license terms |

The model is downloaded from its provider at revision
`344d602b128d1bbdacb43b08d0a3626f46343e29`. No model weights, engine binaries,
CUDA/TensorRT packages, or copies of the upstream repositories are bundled.
The examined Edge-LLM source revision during original setup was
`95515c2f87fba8982db5a519f9022277667b3cc9`; installed runtime version was 0.11.0.

Original work packaged here consists of setup glue, model-view preparation,
process management, measurement instrumentation, and documentation. NVIDIA's
frontend and model inference remain upstream components. Coding and setup
were AI-assisted. References to NVIDIA identify the components being used;
this project does not imply NVIDIA sponsorship or endorsement.

This repository is a personal technical experiment. It contains no client
data or employer project materials and makes no claim to be an official
company offering. Business use cases discussed elsewhere are future ideas,
not implemented features of this webcam demo.
