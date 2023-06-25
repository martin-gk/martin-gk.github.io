let executionProcess;
const homeBtn = document.getElementById("homeBtn");

const replayBtn = document.getElementById("replayBtn");
const replayScreen = document.getElementById("replayScreen");
const backBtn = document.getElementById("backBtn");
const visualToggle = document.getElementById("visualToggle");
const physicalToggle = document.getElementById("physicalToggle");

const replayBackBtn = document.getElementById("replayBackBtn");
const replayConfirmBtn = document.getElementById("replayConfirmBtn");
const buttonContainer = document.getElementById("buttonContainer");

const visualScreen = document.getElementById("visualScreen");
const visualBackBtn = document.getElementById("visualBackBtn");
const visualConfirmBtn = document.getElementById("visualConfirmBtn");
const buttonGroupVisual = document.getElementById("buttonGroupVisual");
const selectWheelV = document.getElementById("selectWheelV");
const selectWheelPV = document.getElementById("selectWheelPV");

const physicalScreen = document.getElementById("physicalScreen");
const physicalBackBtn = document.getElementById("physicalBackBtn");
const physicalStartBtn = document.getElementById("physicalStartBtn");
const physicalVisualStartBtn = document.getElementById(
  "physicalVisualStartBtn"
);
const physicalStartBtns = document.querySelectorAll(".physicalStartBtn");
physicalStartBtns.forEach(function (btn) {
  btn.addEventListener("click", startScript);
});

const videoContainer = document.getElementById("videoContainer");
const videoContent = document.getElementById("videoContent");
const videoBackBtn = document.getElementById("videoBackBtn");
const videoDescriptionUni = document.getElementById("videoDescriptionUni");
const videoDescriptionMur = document.getElementById("videoDescriptionMur");

const trackBtn = document.getElementById("trackBtn");
const trackScreen = document.getElementById("trackScreen");
const trackBackBtn = document.getElementById("trackBackBtn");
const trackConfirmBtn = document.getElementById("trackConfirmBtn");

const liveBtn = document.getElementById("liveBtn");
const liveScreen = document.getElementById("liveScreen");
const liveBackBtn = document.getElementById("liveBackBtn");
const liveConfirmBtn = document.getElementById("liveConfirmBtn");

const physicalVisualScreen = document.getElementById("physicalVisualScreen");
const physicalVisualBackBtn = document.getElementById("physicalVisualBackBtn");
const physicalVisualConfirmBtn = document.getElementById(
  "physicalVisualConfirmBtn"
);
const videoPhysicalBackBtn = document.getElementById("videoPhysicalBackBtn");
const buttonGroupPhysicalVisual = document.getElementById(
  "buttonGroupPhysicalVisual"
);

visualToggle.checked = false;

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    this.classList.toggle("active");

    /* Toggle between hiding and showing the active panel */
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}

homeBtn.addEventListener("click", function () {
  // Reset to the first screen
  replayScreen.style.display = "none";
  buttonContainer.style.display = "flex";
  visualScreen.style.display = "none";
  visualToggle.checked = false;
  physicalToggle.checked = false;
  videoContainer.style.display = "none";
  videoBackBtn.style.display = "none";
  physicalScreen.style.display = "none";
  trackScreen.style.display = "none";
  liveScreen.style.display = "none";
  physicalVisualScreen.style.display = "none";
});

replayBtn.addEventListener("click", function () {
  replayScreen.style.display = "block";
  buttonContainer.style.display = "none";
  visualScreen.style.display = "none";
  visualToggle.checked = false;
  physicalScreen.style.display = "none";
  physicalVisualScreen.style.display = "none";
  physicalToggle.checked = false;
  homeBtn.style.display = "block";
  replayBackBtn.style.display = "block";
  replayConfirmBtn.style.display = "block";
});

replayBackBtn.addEventListener("click", function () {
  replayScreen.style.display = "none";
  buttonContainer.style.display = "flex";
});

replayConfirmBtn.addEventListener("click", function () {
  if (visualToggle.checked && physicalToggle.checked == false) {
    visualScreen.style.display = "block";
    replayScreen.style.display = "none";
    replayBackBtn.style.display = "none";
    replayConfirmBtn.style.display = "none";
    visualBackBtn.style.display = "block";
    visualConfirmBtn.style.display = "block";
    homeBtn.style.display = "block";
  }
  if (physicalToggle.checked && visualToggle.checked) {
    physicalVisualScreen.style.display = "block";
    replayScreen.style.display = "none";
    replayBackBtn.style.display = "none";
    replayConfirmBtn.style.display = "none";
    physicalVisualBackBtn.style.display = "block";
    physicalVisualConfirmBtn.style.display = "block";
  }
  if (physicalToggle.checked && visualToggle.checked == false) {
    physicalScreen.style.display = "block";
    replayScreen.style.display = "none";
    replayBackBtn.style.display = "none";
    replayConfirmBtn.style.display = "none";
    physicalBackBtn.style.display = "block";
    physicalStartBtn.style.display = "block";
  }
  if (physicalToggle.checked == false && visualToggle.checked == false) {
    alert("You have to choose at least one option!");
  } else {
    visualToggle.checked = false;
    physicalToggle.checked = false;
  }
});

physicalBackBtn.addEventListener("click", function () {
  visualScreen.style.display = "none";
  physicalVisualScreen.style.display = "none";
  physicalScreen.style.display = "none";
  replayScreen.style.display = "block";
  visualToggle.checked = false;
  physicalToggle.checked = false;
  replayBackBtn.style.display = "block";
  replayConfirmBtn.style.display = "block";
});

//------ Script Logic

function startScript() {
  if (
    physicalStartBtn.textContent === "Start Suit" ||
    physicalVisualStartBtn.textContent === "Start Suit"
  ) {
    fetch("/execute-script")
      .then((response) => response.text())
      .then((message) => {
        console.log(message);
        // Store the execution process ID returned from the server
        executionProcess = message;
        physicalStartBtn.textContent = "Stop Suit";
        physicalVisualStartBtn.textContent = "Stop Suit";
      })
      .catch((error) => console.error(error));
  } else if (
    physicalStartBtn.textContent === "Stop Suit" ||
    physicalVisualStartBtn.textContent === "Stop Suit"
  ) {
    if (executionProcess) {
      fetch(`/stop-script?pid=${executionProcess}`)
        .then((response) => response.text())
        .then((message) => {
          console.log(message);
          // Reset the execution process variable
          executionProcess = null;
          physicalStartBtn.textContent = "Start Suit";
          physicalVisualStartBtn.textContent = "Start Suit";
        })
        .catch((error) => console.error(error));
    }
  }
}
//------

physicalVisualBackBtn.addEventListener("click", function () {
  visualScreen.style.display = "none";
  physicalVisualScreen.style.display = "none";
  physicalScreen.style.display = "none";
  replayScreen.style.display = "block";
  visualToggle.checked = false;
  physicalToggle.checked = false;
  replayBackBtn.style.display = "block";
  replayConfirmBtn.style.display = "block";
});

physicalVisualConfirmBtn.addEventListener("click", function () {
  if (selectWheelPV.value == "uniPV") {
    videoContainer.style.display = "block";
    videoDescriptionUni.style.display = "block";
    videoDescriptionMur.style.display = "none";
    videoContent.innerHTML =
      '<video width="560" height="315" src="test.mp4" controls></video>';
    physicalVisualScreen.style.display = "none";
    physicalVisualBackBtn.style.display = "none";
    physicalVisualConfirmBtn.style.display = "none";
    buttonGroupVisual.style.display = "none";
    buttonGroupPhysicalVisual.style.display = "block";
    homeBtn.style.display = "block";
    replayScreen.style.display = "none";
  }
  if (selectWheelPV.value == "murPV") {
    videoContainer.style.display = "block";
    videoDescriptionMur.style.display = "block";
    videoDescriptionUni.style.display = "none";
    videoContent.innerHTML =
      '<iframe width="560" height="315" src="https://www.youtube.com/embed/PlnpRfod6lE" title="Laufen in Graz - Murradweg - 10km Lauf - Zeitraffer - Hyperlapse" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
    physicalVisualScreen.style.display = "none";
    physicalVisualBackBtn.style.display = "none";
    physicalVisualConfirmBtn.style.display = "none";
    buttonGroupVisual.style.display = "none";
    buttonGroupPhysicalVisual.style.display = "block";
    homeBtn.style.display = "block";
    replayScreen.style.display = "none";
  } else {
    // Perform other actions based on the selected option
  }
});

videoPhysicalBackBtn.addEventListener("click", function () {
  videoContainer.style.display = "none";
  physicalVisualScreen.style.display = "block";

  physicalVisualBackBtn.style.display = "block";
  physicalVisualConfirmBtn.style.display = "block";
  videoDescriptionUni.style.display = "none";
  videoDescriptionMur.style.display = "none";
});

visualBackBtn.addEventListener("click", function () {
  visualScreen.style.display = "none";
  physicalScreen.style.display = "none";
  physicalVisualScreen.style.display = "none";
  replayScreen.style.display = "block";
  visualToggle.checked = false;
  replayBackBtn.style.display = "block";
  replayConfirmBtn.style.display = "block";
});

visualConfirmBtn.addEventListener("click", function () {
  if (selectWheelV.value == "uniV") {
    videoContainer.style.display = "block";
    videoDescriptionUni.style.display = "block";
    videoDescriptionMur.style.display = "none";
    videoContent.innerHTML =
      '<video width="560" height="315" src="test.mp4" controls></video>';
    visualScreen.style.display = "none";
    visualBackBtn.style.display = "none";
    visualConfirmBtn.style.display = "none";
    buttonGroupVisual.style.display = "block";
    buttonGroupPhysicalVisual.style.display = "none";
    homeBtn.style.display = "block";
  }
  if (selectWheelV.value == "murV") {
    videoContainer.style.display = "block";
    videoDescriptionMur.style.display = "block";
    videoDescriptionUni.style.display = "none";
    videoContent.innerHTML =
      '<iframe width="560" height="315" src="https://www.youtube.com/embed/PlnpRfod6lE" title="Laufen in Graz - Murradweg - 10km Lauf - Zeitraffer - Hyperlapse" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
    videoBackBtn.style.display = "block";
    visualScreen.style.display = "none";
    visualBackBtn.style.display = "none";
    visualConfirmBtn.style.display = "none";
    buttonGroupVisual.style.display = "block";
    buttonGroupPhysicalVisual.style.display = "none";
    homeBtn.style.display = "block";
  } else {
    // Perform other actions based on the selected option
  }
});

videoBackBtn.addEventListener("click", function () {
  videoContainer.style.display = "none";
  visualScreen.style.display = "block";
  visualBackBtn.style.display = "block";
  visualConfirmBtn.style.display = "block";
  videoDescriptionUni.style.display = "none";
  videoDescriptionMur.style.display = "none";
  buttonGroupPhysicalVisual.style.display = "none";
});

//TRACK - SCREEN
trackBtn.addEventListener("click", function () {
  trackScreen.style.display = "block";
  buttonContainer.style.display = "none";
});

trackBackBtn.addEventListener("click", function () {
  trackScreen.style.display = "none";
  buttonContainer.style.display = "flex";
});

trackConfirmBtn.addEventListener("click", function () {
  alert("Future Work - Please press the back button!");
  //TODO;
});

//LIVE SCREEN
liveBtn.addEventListener("click", function () {
  liveScreen.style.display = "block";
  buttonContainer.style.display = "none";
});

liveBackBtn.addEventListener("click", function () {
  liveScreen.style.display = "none";
  buttonContainer.style.display = "flex";
});

liveConfirmBtn.addEventListener("click", function () {
  alert("Future Work - Please press the back button!");
  //TODO;
});
