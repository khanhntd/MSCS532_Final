
import requests
from pathlib import Path



def createDirSaveFile(dirPath: Path, url: str) -> None:
    """
    Check if the path exists and create it if it does not.
    Check if the file exists and download it if it does not.
    """
    if not dirPath.parents[0].exists():
        dirPath.parents[0].mkdir(parents=True)
        print(f'Directory Created: {dirPath.parents[0]}')
    else:
        print('Directory Exists')

    if not dirPath.exists():
        r = requests.get(url, allow_redirects=True)
        open(dirPath, 'wb').write(r.content)
        print(f'File Created: {dirPath.name}')
    else:
        print('File Exists')

def downloadDataset() -> list[str]:
  twitter = 'https://assets.datacamp.com/production/repositories/580/datasets/64cf6963a7e8005e3771ef3b256812a5797320f0/ego-twitter.p'
  dataDir = Path('data/')
  datasets = [twitter]
  dataPaths = list()
  for data in datasets:
      fileName = data.split('/')[-1].replace('?raw=true', '')
      dataPath = dataDir / fileName
      createDirSaveFile(dataPath, data)
      dataPaths.append(dataPath)

  return dataPaths