# 开机语音

做法和《NABO 赛博算命机》（“NABO，在此恭候”）、《NABO 声音实验室》（“那波，陪你玩音乐！”）一致。

## 用户：在即梦里生成（只做一次）

1. 打开即梦（Dreamina）画布里的文字转语音（Canvas TTS）。
2. 音色选 **阳光小男孩**（和前两个项目同一个音色，NABO 的声音保持一致）。
3. 文本填：

   ```
   那波，陪你遥控万物！
   ```

   写“那波”而不是“NABO”，TTS 才会读成“那波”，不会读成英文字母。
4. 听一遍：语气开朗、语速正常、“遥控万物”四个字清楚。不满意可以再生成一版，选最好的一版。
5. 下载原始文件（mp3），**不要剪、不要转码**，放进 `game-art/toolkit/audio/originals/`，告诉 Claude。

## Claude：处理

```sh
ffmpeg -i originals/<原片>.mp3 \
  -af "highpass=f=90,lowpass=f=6500,loudnorm=I=-16:TP=-3:LRA=7,afade=t=in:d=0.01" \
  -ac 1 -ar 16000 -c:a pcm_s16le boot-welcome.wav
```

- 掐掉首尾静音，总长控制在约 2.5 秒。
- 写 `generation.json`：生成器、文本、音色、原片文件名和 SHA256、处理参数、运行时说明（进入开机画面 1400 ms 后播放，其他提示音压到四分之一）。参考算命机的 `game-art/fortune/audio/generation.json`。
- 检查：波形不削顶，结尾回到静音；在原型里试听。
- 原片保留，不覆盖；之后不要重复付费生成。
