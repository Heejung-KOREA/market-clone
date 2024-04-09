//게시글 등록한 시간 가져오는 함수
const calcTime = (timestamp) => {
    //세계 시간 기준으로 맞춰줌. 한국시간은 UTC+0 이므로 9시간을 빼주면 된다.
    const curTime = new Date().getTime() - 9 * 60 * 60 * 1000;
    const time = new Date(curTime - timestamp);
    const hour = time.getHours();
    const minute = time.getMinutes();
    const second = time.getSeconds();

    if (hour > 0) return `${hour}시간 전`
    else if (minute > 0) return `${minute}분 전`;
    else if (second > 0) return `${second}초 전`;
    else return '방금 전';
};

const renderData = (data) => {
    const main = document.querySelector("main");
    data.reverse().forEach(async (obj) => {   //reverse() --> 새로 입력한 글을 위에 올라오게 해줌
        const div = document.createElement("div");
        div.className = "item-list";

        const imgDiv = document.createElement("div");
        imgDiv.className = "item-list__img";

        const img = document.createElement("img");
        const res = await fetch(`/images/${obj.id}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        img.src = url;

        const InfoDiv = document.createElement("div");
        InfoDiv.className = "item-list__info";

        const InfoTitleDiv = document.createElement("div");
        InfoTitleDiv.className = "item-list__info-title";
        InfoTitleDiv.innerHTML = obj.title;

        const InfoMetaDiv = document.createElement("div");
        InfoMetaDiv.className = "item-list__info-meta";
        InfoMetaDiv.innerHTML = obj.place + " " + calcTime(obj.insertAt);

        const InfoPriceDiv = document.createElement("div");
        InfoPriceDiv.className = "item-list__info-price";
        InfoPriceDiv.innerHTML = obj.price;

        imgDiv.appendChild(img);
        InfoDiv.appendChild(InfoTitleDiv);
        InfoDiv.appendChild(InfoMetaDiv);
        InfoDiv.appendChild(InfoPriceDiv);

        div.appendChild(imgDiv);
        div.appendChild(InfoDiv); //최상단 div에 다 넣어줌

        main.appendChild(div);
    });
};

const fetchList = async () => {
    const res = await fetch("/items");
    const data = await res.json();
    renderData(data);
};

fetchList();

