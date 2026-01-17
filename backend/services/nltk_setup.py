"""
NLTK Data Setup - 确保所有需要的数据都已下载
在应用启动时运行，自动下载缺失的数据
"""
import nltk
import os
import sys

# NLTK 数据存储路径
NLTK_DATA_DIR = '/usr/local/share/nltk_data'

# 确保数据目录在搜索路径中
if NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.insert(0, NLTK_DATA_DIR)

# 需要的所有 NLTK 数据包（兼容新旧版本）
REQUIRED_PACKAGES = [
    # 分词器
    ('tokenizers/punkt', 'punkt'),
    ('tokenizers/punkt_tab', 'punkt_tab'),
    
    # 停用词
    ('corpora/stopwords', 'stopwords'),
    
    # 词性标注
    ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
    ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
    
    # 词形还原（可选，但建议有）
    ('corpora/wordnet', 'wordnet'),
    ('corpora/omw-1.4', 'omw-1.4'),
]

def download_nltk_data():
    """下载所有需要的 NLTK 数据"""
    print("🔍 Checking NLTK data...")
    
    missing_packages = []
    
    for resource_path, package_name in REQUIRED_PACKAGES:
        try:
            nltk.data.find(resource_path)
            print(f"✅ {package_name} - Found")
        except LookupError:
            print(f"⚠️  {package_name} - Missing, will download")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n📥 Downloading {len(missing_packages)} missing packages...")
        
        for package in missing_packages:
            try:
                print(f"   Downloading {package}...", end=" ")
                nltk.download(
                    package, 
                    download_dir=NLTK_DATA_DIR,
                    quiet=True
                )
                print("✅")
            except Exception as e:
                print(f"❌ Failed: {e}")
                # 不要因为单个包失败而停止整个应用
                continue
        
        print("✅ NLTK data setup complete!\n")
    else:
        print("✅ All NLTK data already present\n")

# 启动时自动运行
if __name__ == "__main__":
    download_nltk_data()
else:
    # 作为模块导入时也运行（但只运行一次）
    try:
        download_nltk_data()
    except Exception as e:
        print(f"⚠️  NLTK setup warning: {e}")
        # 继续运行，不要阻止应用启动
