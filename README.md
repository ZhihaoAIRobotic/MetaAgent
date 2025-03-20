
<p align="center">
  <a href="https://github.com/ZhihaoAIRobotic/MetaAgent//#gh-light-mode-only">
    <img src="Docs/resource/MetaAgent-logo-black.png" width="418px" alt="logo" />
  </a>
  <a href="https://github.com/ZhihaoAIRobotic/MetaAgent//#gh-dark-mode-only">
    <img src="Docs/resource/MetaAgent-logo-white.png" width="418px" alt="logo" />
  </a>
</p>

<p align="center"><i>:unicorn: The next generation of Multi-Modal Multi-Agent framework. :robot:. </i></p>

## Introduction
We are dedicated to developing a universal **multi-modal multi-agent** framework. Multi-modal agents are very powerful agents capable of **understanding and generating** information **across various modalities**—including text, images, audio, and video. These agents are designed to **automatically completing complex tasks** that involve multiple modals of input and output. Our Framework also aims to support **multi-agent collaboration**. This approach allows for a more comprehensive and nuanced understanding of complex scenarios, leading to more effective problem-solving and task completion. 

#### :fire: Features
- Build, manage and deploy your AI agents.

- Multi-modal agents, agents can interact with users using texts, audios, images, and videos. 

- Vector database and knowledge embeddings

- UI for chatting with AI agents.

- Multi-agent collaboration, you can create a agents company for complex tasks, such as draw comics. (Coming soon)

- Fine-tuning and RLHF (Coming soon)

- ChatUI, support multiple sessions.
  ![alt text](<Docs/resource/Multiple sessions.gif>)

  ![alt text](<Docs/resource/graph_demo.gif>)

#### :fire: Framework
![alt text](<Docs/resource/MetaAgent Framewore.png>)


#### :page_with_curl: Examples
Comics Company, create a comic about Elon lands on mars.

![图片9](https://github.com/ZhihaoAIRobotic/MetaAgent/assets/25542404/fb37f50a-b325-4747-82ed-a968ec030112)


Multi-modal agent, draw images and make videos for you.

<img src="Docs/resource/elon.jpg" width="256" height="260">

![Elon](Docs/resource/output.gif)


## Installation
### Package install
Make sure your python version is 3.10 and cuda version is 12.2
```
git clone https://github.com/ZhihaoAIRobotic/MetaAgent.git
conda create -n metaagent python=3.10
conda activate metaagent
poetry install  
```
### TTS Install
- KokoroTTS
```
Installation Tutorial: https://huggingface.co/hexgrad/Kokoro-82M#usage
```
- ParlerTTS
```
poetry install
```

### Frontend install
```
cd frontend
npm install
```

