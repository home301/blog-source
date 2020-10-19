## **MKDocs 로 블로그 만들기**
SSG로 삽질하면서 기록을 남깁니다. 

SSG가 뭐지 하는 호기심에 일단 접근해 보았다.<br/>
국내 검색 뭐시기는 SSG 하면 모 쇼핑 사이트만 나와서...<br/>
구글신님께 아래 기도분으로 기원!

```ssg comparison```

여러 결과 중에서 알록달록하고 그런데로 보기 편하게 비교해 뒀다.
- https://jamstack.org/generators/ 

python도 구경하는데 중인데... mk?? 이거 예전에 쓰던 이름 이니셜이랑 비슷한 느낌??<br/>
아재적인 판단이란 전혀 근거없고 지극히 개인휘향에 따르는 충동적인 것!

### **Mkdocs**
- [mkdocs home](https://www.mkdocs.org/)
- [mkdocs git](https://github.com/mkdocs/mkdocs/)
- [plugins](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#navigation--page-building)

### **설치**
딱히 설명을 남길 것도 없다.
- python 설치 하고 pip 확인. 버전은 3.5 이상.
- ```pip install mkdocs```

더 이상 설명은 생략한다.

### **그리고**
**최초 생성**
- mkdocs로 new 해서 project 만든다.
``` mkdocs new project```

**아래는 반복**
- 생성된 project 내에서 마크 다운으로 뭔가 작성한다.
- mkdocs.yml 갱신
- ```mkdocs build``` 로 static page 생성한다.
- ```mkdocs serve``` 로 생성된 사이트를 구경할 수 있다. port는 ```8000```
- ```./site``` 내부에 있는 생성된 static page를 필요한 곳으로 올린다. 

### **installed plugins**

#### ****
- https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin


