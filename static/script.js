function updateStatus() {

    fetch("/status")

        .then(response => response.json())

        .then(data => {

            const status =
                document.getElementById("status");

            const statusText =
                document.getElementById("status-text");

            const statusBox =
                document.getElementById("status-box");

            const statusIcon =
                document.getElementById("status-icon");


            const eye =
                document.getElementById("eye");

            const mouth =
                document.getElementById("mouth");

            const alerts =
                document.getElementById("alerts");


            const eyeProgress =
                document.getElementById("eye-progress");

            const mouthProgress =
                document.getElementById("mouth-progress");


            eye.innerText =
                data.eye.toFixed(2);

            mouth.innerText =
                data.mouth.toFixed(2);

            alerts.innerText =
                data.alerts;


            /* Eye progress */

            let eyeWidth =
                Math.min(data.eye * 250, 100);

            eyeProgress.style.width =
                eyeWidth + "%";


            /* Mouth progress */

            let mouthWidth =
                Math.min(data.mouth * 150, 100);

            mouthProgress.style.width =
                mouthWidth + "%";


            /* Status */

            if (data.sleepy) {

                status.innerText =
                    "SLEEPY";

                statusText.innerText =
                    "Drowsiness detected!";

                statusIcon.innerText =
                    "!";

                statusBox.classList.remove(
                    "awake"
                );

                statusBox.classList.add(
                    "sleepy"
                );

            }

            else {

                status.innerText =
                    "AWAKE";

                statusText.innerText =
                    "Driver is alert";

                statusIcon.innerText =
                    "✓";

                statusBox.classList.remove(
                    "sleepy"
                );

                statusBox.classList.add(
                    "awake"
                );

            }

        })

        .catch(error => {

            console.log(
                "Status error:",
                error
            );

        });

}


/* Update every 300 milliseconds */

setInterval(
    updateStatus,
    300
);


/* Initial update */

updateStatus();