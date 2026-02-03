import fasttext
import fasttext.util
import numpy as np
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.utils.utils import load_config
CONFIG = load_config()
if not os.path.exists(CONFIG["fastText"]["model_path"]):
    fasttext.util.download_model('en', if_exists='ignore')
    ##删除当前目录下的cc.en.300.bin.gz
    os.remove(CONFIG["fastText"]["model_name"]+".gz")
    ##下载的模型移动到model_data目录下
    os.replace(CONFIG["fastText"]["model_name"], CONFIG["fastText"]["model_path"])

model = fasttext.load_model(CONFIG["fastText"]["model_path"])
print(model.get_word_vector("apple")[:10])
print(model.get_word_vector("apples")[:10])
