const form = document.getElementById('write-form');

const handleSubmitForm = async (event) => {
    event.preventDefault();
    //시간 값 넣어주기(세계시간 기준)
    const body = new FormData(form);
    body.append('insertAt', new Date().getTime());

    try {
        const res = await fetch('/items', {
            method: 'POST',
            body,
        });
        const data = await res.json();
        if (data === '200') window.location.pathname = "/";
    } catch (e) {
        console.error(e);
    }
}

form.addEventListener('submit', handleSubmitForm);

