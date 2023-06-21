//const menuBtn = document.getElementById("menuBtn");
//const menu = document.getElementById("menu");
const homeBtn = document.getElementById("homeBtn");
const replayBtn = document.getElementById("replayBtn");
const replayScreen = document.getElementById("replayScreen");
const backBtn = document.getElementById("backBtn");
const visualToggle = document.getElementById("visualToggle");
const physicalToggle = document.getElementById("physicalToggle");
const visualScreen = document.getElementById("visualScreen");
const visualBackBtn = document.getElementById("visualBackBtn");
const visualConfirmBtn = document.getElementById("visualConfirmBtn");
const replayBackBtn = document.getElementById("replayBackBtn");
const replayConfirmBtn = document.getElementById("replayConfirmBtn");
const buttonContainer = document.getElementById("buttonContainer");

const selectWheel = document.getElementById("selectWheel");
const physicalScreen = document.getElementById("physicalScreen");
const physicalBackBtn = document.getElementById("physicalBackBtn");
const physicalConfirmBtn = document.getElementById("physicalConfirmBtn");
const phyVisSelectionError = document.getElementById("phyVisSelectionError");

const videoContainer = document.getElementById("videoContainer");
const videoContent = document.getElementById("videoContent");
const videoBackBtn = document.getElementById("videoBackBtn");
const videoResetBtn = document.getElementById("videoResetBtn");
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

//const settingsBtn = document.getElementById("settingsBtn");
//menu.classList.add("settingsBtn");

/*menuBtn.addEventListener("click", function () {
/  menu.classList.toggle("show");
});
*/

/*settingsBtn.addEventListener("click", function () {
	//open settins screen here
});
*/

visualToggle.checked = false; // Uncheck the visual toggle initially
visualScreen.style.display = "none"; // Hide the visual screen initially
let sortOfrun;

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
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
  videoContainer.innerHTML = ""; // Clear the embedded video if present
  videoBackBtn.style.display = "none";
  physicalScreen.style.display = "none";
  trackScreen.style.display = "none";
});



replayBtn.addEventListener("click", function () {
  replayScreen.style.display = "block";
  buttonContainer.style.display = "none";
  visualScreen.style.display = "none"; // Hide the visual screen when navigating to the replay screen
  visualToggle.checked = false; // Uncheck the visual toggle when navigating to the replay screen
  physcalScreen.style.display = "none"; // Hide the visual screen when navigating to the replay screen
  physicalToggle.checked = false; 
  phyVisSelectionError.style.display = "none";
  homeBtn.style.display = "block"; // Hide home button
  replayBackBtn.style.display = "block"; // Show replay "Back" button
  replayConfirmBtn.style.display = "block"; // Show replay "Confirm" button
});

replayBackBtn.addEventListener("click", function () {
  replayScreen.style.display = "none";
  phyVisSelectionError.style.display = "none";
  buttonContainer.style.display = "flex";
});

replayConfirmBtn.addEventListener("click", function () {
  if ((visualToggle.checked) && (physicalToggle.checked == false)) {
    visualScreen.style.display = "block";
	phyVisSelectionError.style.display = "none";
    replayScreen.style.display = "none"; // Hide the replay screen
    replayBackBtn.style.display = "none"; // Hide the replay "Back" button
    replayConfirmBtn.style.display = "none"; // Hide the replay "Confirm" button
    visualBackBtn.style.display = "block"; // Show the visual "Back" button
    visualConfirmBtn.style.display = "block"; // Show the visual "Confirm" button
    homeBtn.style.display = "block"; // Hide home button
  } if ((physicalToggle.checked) && (visualToggle.checked)) {
	  physicalScreen.style.display = "block"; 
	  phyVisSelectionError.style.display = "none";
	  replayScreen.style.display = "none"; // Hide the replay screen
      replayBackBtn.style.display = "none"; // Hide the replay "Back" button
      replayConfirmBtn.style.display = "none";
	  physicalBackBtn.style.display = "block";
  } else {
	  phyVisSelectionError.style.display = "block";
	  visualToggle.checked = false;
	  physicalToggle.checked = false;
  }
});

physicalBackBtn.addEventListener("click", function () {
	visualScreen.style.display = "none";
	physicalScreen.style.display = "none";
	phyVisSelectionError.style.display = "none";
	replayScreen.style.display = "block";
	visualToggle.checked = false;
	physicalToggle.checked = false; 
	replayBackBtn.style.display = "block"; // Hide the replay "Back" button
	replayConfirmBtn.style.display = "block";
});

physicalConfirmBtn.addEventListener("click", function () {
	//TODO
});

visualBackBtn.addEventListener("click", function () {
  visualScreen.style.display = "none";
  physicalScreen.style.display = "none";
  replayScreen.style.display = "block";
  visualToggle.checked = false;
  phyVisSelectionError.style.display = "none";
  replayBackBtn.style.display = "block"; // Hide the replay "Back" button
  replayConfirmBtn.style.display = "block"; // Hide the replay "Confirm" button
});

visualConfirmBtn.addEventListener("click", function () {
  // Perform actions when the "Confirm" button is clicked in the "Visual" screen
  const selectedOption = selectWheel.value;
  if (selectedOption === "uni") {
    // Embed the YouTube video
	sortOfrun = "uni";
	videoContainer.style.display = "block";
	videoDescriptionUni.style.display = "block";
    videoContent.innerHTML =
      '<iframe width="560" height="315" src="https://www.youtube.com/embed/MTbEwqNTW4U" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
    visualScreen.style.display = "none";
    visualBackBtn.style.display = "none"; // Show the visual "Back" button
    visualConfirmBtn.style.display = "none"; // Show the visual "Confirm" button
    homeBtn.style.display = "block"; // Show the home button when the video is displayed
  } 
  if(selectedOption == "mur") {
	sortOfrun = "mur";
	videoContainer.style.display = "block";
	videoDescriptionMur.style.display = "block";
	videoContent.innerHTML =
      '<iframe width="560" height="315" src="https://www.youtube.com/embed/PlnpRfod6lE" title="Laufen in Graz - Murradweg - 10km Lauf - Zeitraffer - Hyperlapse" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
	videoBackBtn.style.display = "block";
	videoResetBtn.style.display = "block";
	visualScreen.style.display = "none";
    visualBackBtn.style.display = "none"; // Show the visual "Back" button
    visualConfirmBtn.style.display = "none"; // Show the visual "Confirm" button
    homeBtn.style.display = "block"; // Show the home button when the video is displayed
	
  }else {
    // Perform other actions based on the selected option
  }
});

videoBackBtn.addEventListener("click", function () {
   videoContainer.style.display = "none";
   visualScreen.style.display = "block";
   //videoContainer.innerHTML = ""; 
   visualBackBtn.style.display = "block";
   visualConfirmBtn.style.display = "block";
   videoDescriptionUni.style.display = "none";
   videoDescriptionMur.style.display = "none";
})

videoResetBtn.addEventListener("click", function() {
	videoContainer.style.display = "block";
	if (sortOfrun === "mur"){
		videoContent.innerHTML =
        '<iframe width="560" height="315" src="https://www.youtube.com/embed/PlnpRfod6lE" title="Laufen in Graz - Murradweg - 10km Lauf - Zeitraffer - Hyperlapse" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
	} if (sortOfrun == "uni") {
	    videoContent.innerHTML =
        '<iframe width="560" height="315" src="https://www.youtube.com/embed/MTbEwqNTW4U" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
	}else {}
})


//LIVE - SCREEN
trackBtn.addEventListener("click", function () {
	trackScreen.style.display = "block";
	buttonContainer.style.display = "none";
});

trackBackBtn.addEventListener("click", function () {
	trackScreen.style.display = "none";
	buttonContainer.style.display = "flex";
});

trackConfirmBtn.addEventListener("click", function () {
	//TODO;
});


//TRACK SCREEN
liveBtn.addEventListener("click", function () {
	liveScreen.style.display = "block";
	buttonContainer.style.display = "none";
});

liveBackBtn.addEventListener("click", function () {
	liveScreen.style.display = "none";
	buttonContainer.style.display = "flex";
});

liveConfirmBtn.addEventListener("click", function () {
	//TODO;
});
