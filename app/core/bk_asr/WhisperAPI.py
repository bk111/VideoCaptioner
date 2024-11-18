import os
from typing import Optional

from openai import OpenAI
from ..utils.logger import setup_logger

from .ASRData import ASRDataSeg
from .BaseASR import BaseASR

logger = setup_logger("whisper_api")


class WhisperAPI(BaseASR):
    def __init__(self, 
                 audio_path: str,
                 model: str,
                 language: str = "zh",
                 prompt: str = "",
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None, 
                 use_cache: bool = False):
        """
        初始化 WhisperASR
        
        Args:
            audio_path: 音频文件路径
            model: 模型名称
            language: 语言代码,默认中文
            prompt: 提示词
            base_url: API基础URL,可选
            api_key: API密钥,可选
            use_cache: 是否使用缓存
        """
        super().__init__(audio_path, use_cache)
        
        # 优先使用传入的参数,否则使用环境变量
        self.base_url = base_url
        self.api_key = api_key
        
        if not self.base_url or not self.api_key:
            raise ValueError("必须设置 OPENAI_BASE_URL 和 OPENAI_API_KEY")
            
        self.model = model
        self.language = language
        self.prompt = prompt
        
        logger.info(f"初始化 WhisperASR: model={model}, language={language}")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def _run(self, callback=None) -> dict:
        """执行语音识别"""
        return self._submit()

    def _make_segments(self, resp_data: dict) -> list[ASRDataSeg]:
        """从响应数据构建语音片段"""
        segments = []
        for seg in resp_data['segments']:
            segments.append(ASRDataSeg(
                text=seg['text'].strip(),
                start_time=int(float(seg['start'])*1000),
                end_time=int(float(seg['end'])*1000)
            ))
        return segments

    def _get_key(self) -> str:
        """获取缓存键值"""
        return f"{self.__class__.__name__}-{self.model}-{self.crc32_hex}-{self.language}"

    def _submit(self) -> dict:
        """提交音频进行识别"""
        try:
            logger.info("开始识别音频...")
            completion = self.client.audio.transcriptions.create(
                model=self.model,
                temperature=0,
                response_format="verbose_json",
                file=("audio.mp3", self.file_binary, "audio/mp3"),
                prompt=self.prompt,
                language=self.language
            )
            logger.info("音频识别完成")
            print(completion)
            print("-"*100)
            print(completion.to_dict())
            return completion.to_dict()
        except Exception as e:
            logger.exception(f"音频识别失败: {str(e)}")
            raise e


if __name__ == '__main__':
    # Example usage
    os.environ['OPENAI_BASE_URL'] = "https://api.groq.com/openai/v1"
    os.environ['OPENAI_API_KEY'] = "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"
    audio_file = r"C:\Users\weifeng\Music\output_001.mp3"
    asr = WhisperASR(audio_file, model="whisper-large-v3", language="zh", prompt="", use_cache=False)
    asr_data = asr.run()
    print(asr_data)
