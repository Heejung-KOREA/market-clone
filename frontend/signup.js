const form = document.querySelector("#signup-form");

const checkPassword = () => {
    const formData = new FormData(form);
    const password = formData.get("password");
    const password2 = formData.get("password2");

    if (password === password2) {
        return true;
    } else return false;
};

const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    //formdata에서 password 값을 가져와서 sha256으로 보완을 해줌
    const sha256Password = sha256(formData.get("password"));
    formData.set("password", sha256Password);

    const div = document.querySelector("#info");

    if (checkPassword()) {   //비밀번호 확인 결과 두개의 값이 같다면, 요청을 보냄
        const res = await fetch("/signup", {
            method: "post",
            body: formData,
        });
        const data = await res.json();
        if (data === "200") {   //서버에서 응답을 줬을때만 변경
            // div.innerText = "회원가입 성공";
            // div.style.color = "blue";
            alert('회원 가입에 성공했습니다.');
            window.location.pathname = "/login.html"; //로그인 페이지로 이동
        }
    } else {
        div.innerText = "비밀번호가 같지 않습니다.";
        div.style.color = "red";
    }

};

form.addEventListener("submit", handleSubmit);

