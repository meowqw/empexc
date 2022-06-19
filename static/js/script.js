// добавление резюме
document.getElementById("saveResume").onclick = async function () {

    let resume = {
        fname: document.getElementById('fname').value,
        mname: document.getElementById('mname').value,
        lname: document.getElementById('lname').value,
        city: document.getElementById('city').value,
        date: document.getElementById('date').value,
        profession: document.getElementById('profession').value,
        skills: document.getElementById('skills').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        info: document.getElementById('info').value
    };

    // выполение запроса на добавление
    let response = await fetch('/resume_add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(resume)
    });

    document.getElementById('popup-add-resume').className = "popup";
    resumeLoad();
}

// удалить резюме
delResume = async function (id) {
    resume = await fetch('/resume_del/' + id).then(response => { return response.json() }).then((json) => {
        return json;
    });

    resumeLoad();
    document.getElementById('popup-resume').className = "popup";

}

// открыть резюме
openResume = async function (id) {
    resume = await fetch('/resume/' + id).then(response => { return response.json() }).then((json) => {
        return json;
    });

    authStatus = await fetch('/check_auth').then(response => { return response.json() }).then((json) => {
        return json;
    });

    document.getElementById('Rfname').innerHTML = resume['fname'];
    document.getElementById('RFfname').innerHTML = resume['fname'];
    document.getElementById('Rmname').innerHTML = resume['mname'];
    document.getElementById('Rlname').innerHTML = resume['lname'];
    document.getElementById('Rcity').innerHTML = resume['city'];
    document.getElementById('Rdate').innerHTML = resume['date'];
    document.getElementById('Rprofession').innerHTML = resume['profession'];
    document.getElementById('Rskills').innerHTML = resume['skills'];
    document.getElementById('Rphone').innerHTML = `<a href="tel:${resume['phone']}">${resume['phone']}</a>`;
    document.getElementById('Remail').innerHTML = `<a href="mailto:${resume["email"]}">${resume["email"]}</a>`;
    document.getElementById('Rinfo').innerHTML = resume['info'];

    if (authStatus['status'] != 'None'){
        document.getElementById('btnResumeDel').innerHTML = `<button class="popup__button button-del" onclick="delResume(${id})">Удалить резюме</button>`
    }
    else {
        document.getElementById('btnResumeDel').innerHTML = ''
    }
    document.getElementById('popup-resume').className = 'popup open';
}

printContent = async function printContent(content) {
    authStatus = await fetch('/check_auth').then(response => { return response.json() }).then((json) => {
        return json;
    });
    html_content = '';
    if (authStatus['status'] != 'None') {
        html_content += `<a href="#popup-add-resume" class="button resume__item item-resume__add popup-link" 
        onclick="document.getElementById('popup-add-resume').className = 'popup open';">
        <div class="item-resume__add-icon">+</div>
        <div class="item-resume__add-text">добавить резюме</div>
        </a>`;
    };
    content.forEach(obj => {
        html_content += `<a href="#popup-resume" class="resume__item button popup-link"
        onclick=openResume(${obj.id})>
        <div class="resume__item-name">${obj.fname} ${obj.mname}</div>
        <div class="resume__item-prof">${obj.profession}</div>
    </a>`
    });

    document.getElementById('resumeList').innerHTML = html_content;
}

// получить все резюме
resumeLoad = async function () {
    content = await fetch('/resume_load').then(response => { return response.json() }).then((json) => {
        return json;
    });

    printContent(content);

}

// получить резуме по профессии
getResumeProf = async function (prof) {
    content = await fetch('/resume_profession/' + prof).then(response => { return response.json() }).then((json) => {
        return json;
    });

    printContent(content);
}

// получить резюме по поиску
document.getElementById('searchBtn').onclick = async function () {
    searchText = document.getElementById('searchInput').value
    content = await fetch('/search/' + searchText).then(response => { return response.json() }).then((json) => {
        return json;
    });

    printContent(content);

}

resumeLoad();
