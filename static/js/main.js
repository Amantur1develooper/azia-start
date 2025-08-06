const API_BASE_URL = "176.57.215.14";

let elCarouselList = document.querySelector(".count__wrapper");
let listFragment = new DocumentFragment();

function GetCount() {
  elCarouselList.innerHTML = "";

  fetch(`http://${API_BASE_URL}:8080/api/school-info`)
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data);
        let newItem = document.createElement("ul");
        newItem.setAttribute("class", "count__cover");
        let info = `
        <li class="count__item">
              ${data.graduateAmount}
              <span> Выпускников </span>
            </li>
            <li class="count__item">
            ${data.branchAmount}
              <span> Филлиала </span>
            </li>
            <li class="count__item">
            ${data.studentAmount}
              <span> Учеников </span>
            </li>
            <li class="count__item">
            ${data.mediumOptScore}
              <span> Средний балл ОРТ </span>
            </li>
        `;
        newItem.innerHTML = info;
        listFragment.appendChild(newItem);
      }
      elCarouselList.appendChild(listFragment);
    })
    .catch((err) => console.log(err));
}

GetCount();

// Get Video
let elVideo = document.querySelector(".about__cover");
let VideoFragment = new DocumentFragment();

function GetVideo() {
  elVideo.innerHTML = "";

  fetch(`http://${API_BASE_URL}:8080/api/video`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data);
        let newItem = document.createElement("div");
        newItem.setAttribute("class", "about__video");
        let info = `
        <iframe
        src="https://www.youtube.com/embed/${data.url}"
        title="Mortal Kombat 1 - Official It’s In Our Blood Trailer ft. Dave Bautista"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
      ></iframe>
        `;
        newItem.innerHTML = info;
        VideoFragment.appendChild(newItem);
      }
      elVideo.appendChild(VideoFragment);
    })
    .catch((err) => console.log(err));
}

GetVideo();

// Get Student
let elStudentList = document.querySelector(".student__list");
let StudentFragment = new DocumentFragment();

function GetStudent() {
  // elStudentList.innerHTML = "";

  fetch(`http://${API_BASE_URL}:8080/api/student/get-all`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data);
        data.forEach((item) => {
          let newItem = document.createElement("li");
          newItem.setAttribute("class", "student__item");
          let info = `
          <div>
          <img
            class="student__img"
            src="http://${API_BASE_URL}/image/${item.image.path}"
            alt="student"
          />
          <div class="item__info">
            <h3 class="item__title">${item.firstName} ${item.lastName}</h3>
            <p class="item__text">${item.level} класс</p>
          </div>
          `;
          newItem.innerHTML = info;
          StudentFragment.appendChild(newItem);
        });
        elStudentList.appendChild(StudentFragment);
      }
    })
    .catch((err) => console.log(err));
}

GetStudent();

// Get News
let elSNewsList = document.querySelector(".news__list");
let NewsFragment = new DocumentFragment();

function GetNews() {
  elSNewsList.innerHTML = "";

  fetch(`http://${API_BASE_URL}:8080/api/news/get-all`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data);
        data.forEach((item) => {
          let newItem = document.createElement("li");
          newItem.setAttribute("class", "student__item");
          let info = `
          <div class="news__wrap">
          <div class="news__info info">
            <h3 class="info__title">
            ${item?.title}
            </h3>
            <p class="info__text">
            ${item?.content}
            </p>
            <span class="info__data">${item?.createdAt}</span>
          </div>

          <div class="news__cover">
            <img
              class="news__img"
              src="http://${API_BASE_URL}/image/${item.image.path}"
              alt="news"
            />
          </div>
        </div>
          `;
          newItem.innerHTML = info;
          NewsFragment.appendChild(newItem);
        });
        elSNewsList.appendChild(NewsFragment);
      }
      $(".news__list").slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        dots: true,
        autoplay: true,
        autoplaySpeed: 5000,
      });
    })
    .catch((err) => console.log(err));
}

GetNews();

// why Us

let elBtnOne = document.querySelector(".item__plus--one");
let elBtnTwo = document.querySelector(".item__plus--two");
let elBtnThree = document.querySelector(".item__plus--three");
let elBtnFour = document.querySelector(".item__plus--four");
let elBtnFive = document.querySelector(".item__plus--five");
let elBoxOne = document.querySelector(".item__box--one");
let elBoxTwo = document.querySelector(".item__box--two");
let elBoxThree = document.querySelector(".item__box--three");
let elBoxFour = document.querySelector(".item__box--four");
let elBoxFive = document.querySelector(".item__box--five");

elBtnOne.addEventListener("click", function () {
  elBoxOne.classList.add("showing");
});
elBoxOne.addEventListener("click", function () {
  elBoxOne.classList.remove("showing");
});
// second
elBtnTwo.addEventListener("click", function () {
  elBoxTwo.classList.add("showing");
});
elBoxTwo.addEventListener("click", function () {
  elBoxTwo.classList.remove("showing");
});

// three
elBtnThree.addEventListener("click", function () {
  elBoxThree.classList.add("showing");
});
elBoxThree.addEventListener("click", function () {
  elBoxThree.classList.remove("showing");
});
// four
elBtnFour.addEventListener("click", function () {
  elBoxFour.classList.add("showing");
});
elBoxFour.addEventListener("click", function () {
  elBoxFour.classList.remove("showing");
});
// five
elBtnFive.addEventListener("click", function () {
  elBoxFive.classList.add("showing");
});
elBoxFive.addEventListener("click", function () {
  elBoxFive.classList.remove("showing");
});

// header drop

elHeaderDroop = document.querySelector(".header__drop");
elOpenDroopBtn = document.querySelector(".sent__btn");
elCloseDroopBtn = document.querySelector(".drop__exit");

elOpenDroopBtn.addEventListener("click", function () {
  elHeaderDroop.classList.add("header__drop--on");
});
elCloseDroopBtn.addEventListener("click", function () {
  elHeaderDroop.classList.remove("header__drop--on");
});
elHeaderDroop.addEventListener("click", function (evt) {
  if (evt.target.className === "header__drop drop header__drop--on") {
    elHeaderDroop.classList.remove("header__drop--on");
  }
});

// Modl form

elModal = document.querySelector(".modal");
elOpenModalBtn = document.querySelector(".hero__btn");
elSecondOpenModalBtn = document.querySelector(".item__btn");
elCloseModalBtn = document.querySelector(".info__exit");

elOpenModalBtn.addEventListener("click", function () {
  elModal.classList.add("modal-on");
});

elSecondOpenModalBtn.addEventListener("click", function () {
  elModal.classList.add("modal-on");
});

// elCloseModalBtn.addEventListener("click", function () {
//   elModal.classList.remove("modal-on");
// });

// form submit

// Add contact

let elForm = document.querySelector(".info__form");
let elInputName = document.querySelector(".form__input--name");
let elInputSurname = document.querySelector(".form__input--surname");
let elInputClass = document.querySelector(".form__input--class");
let elInputPhone = document.querySelector(".form__input--phone");

elForm.addEventListener("submit", function (evt) {
  evt.preventDefault();

  let inputName = elInputName.value;
  let inputSurname = elInputSurname.value;
  let inputClass = elInputClass.value;
  let inputPhone = elInputPhone.value;

  if (
    elInputName.value &&
    elInputSurname.value &&
    elInputClass.value &&
    elInputPhone.value
  ) {
    fetch(`http://${API_BASE_URL}:8080/api/applicant`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        firstName: inputName,
        lastName: inputSurname,
        level: inputClass,
        phoneNumber: inputPhone,
      }),
    })
      .then((data) => {
        if (data.status === 200) {
          // elModal.classList.remove("modal-on");
          elInputName.value = "";
          elInputSurname.value = "";
          elInputClass.value = "";
          elInputPhone.value = "";
          alert("Ваша заявка отправлена!");
        }
      })
      .catch((err) => console.log(err));
  } else {
    alert("Пожалуйста, заполните все данные!");
  }
});

// get teacher

let elTeacherList = document.querySelector(".teacher__list");
let TeacherFragment = new DocumentFragment();

function GetTeacher() {
  elTeacherList.innerHTML = "";

  fetch(`http://${API_BASE_URL}:8080/api/subject/get-all`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data);
        data
          .filter((e) => e.name !== null && e.teacher !== null)
          .forEach((item) => {
            let newItem = document.createElement("li");
            newItem.setAttribute("class", "teacher__item");
            let info = `
          <button class="teacher__button" data-id=${item.id} id="butt">
          ${item?.name}
          </button>
          `;
            newItem.innerHTML = info;
            TeacherFragment.appendChild(newItem);
          });
        elTeacherList.appendChild(TeacherFragment);
      }
    })
    .catch((err) => console.log(err));
}

GetTeacher();

// get user Tech
function GetUser() {
  fetch(`http://${API_BASE_URL}:8080/api/subject/get-all`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        // console.log(data[0]);
        elTeacherInfo.innerHTML = "";
        let newItem = document.createElement("div");
        newItem.setAttribute("class", "right__cover");
        let info = `
              <div class="right__wrap">
                <img
                  class="right__img"
                  src="http://176.57.215.14/image/${data[0]?.teacher?.image?.path}"
                  alt="teacher img"
                />

                <div class="right__info">
                  <h3 class="right__title">${data[0]?.teacher?.firstName}</h3>
                  <span class="right__desc"> ${data[0]?.name} </span>
                  <p class="right__text">
                  ${data[0]?.teacher?.description}
                  </p>
                </div>
              </div>
              `;
        newItem.innerHTML = info;
        InfoFragment.appendChild(newItem);
      }
      elTeacherInfo.appendChild(InfoFragment);
    })
    .catch((err) => console.log(err));
}

GetUser();

// teacher info
let elTeacherBtn = document.querySelector(".teacher__list");
let elTeacherInfo = document.querySelector(".teacher__right");
let InfoFragment = new DocumentFragment();

if (elTeacherBtn) {
  elTeacherBtn.addEventListener("click", function (evt) {
    var elementName = evt.target.textContent.trim();

    fetch(`http://${API_BASE_URL}:8080/api/subject/get-all`, {
      method: "GET",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data) {
          // console.log(data);
          elTeacherInfo.innerHTML = "";
          data?.forEach((e) => {
            if (e?.name === elementName) {
              // console.log(e.teacher.image.data);
              let newItem = document.createElement("div");
              newItem.setAttribute("class", "right__cover");
              let info = `
              <div class="right__wrap">
               
                <img
                class="right__img"
                src="http://176.57.215.14/image/${e?.teacher?.image?.path}"
                alt="teacher"
              />

                <div class="right__info">
                  <h3 class="right__title">${e?.teacher?.firstName}</h3>
                  <span class="right__desc"> ${elementName} </span>
                  <p class="right__text">
                  ${e?.teacher?.description}
                  </p>
                </div>
              </div>
              `;
              newItem.innerHTML = info;
              InfoFragment.appendChild(newItem);
            }
            elTeacherInfo.appendChild(InfoFragment);
          });
        }
      })
      .catch((err) => console.log(err));
  });
}
