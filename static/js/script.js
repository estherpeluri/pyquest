document.addEventListener("DOMContentLoaded", function () {

    const editor = document.getElementById("codeEditor");
    const codeForm = document.getElementById("codeForm");
    const submitButton = document.getElementById("submitButton");


    /* ============================================================
       STOP IF WE ARE NOT ON THE LEVEL PAGE
    ============================================================ */

    if (!editor || !codeForm || !submitButton) {
        return;
    }


    /* ============================================================
       TAB KEY SUPPORT
    ============================================================ */

    editor.addEventListener("keydown", function (event) {

        if (event.key === "Tab") {

            event.preventDefault();

            const start = this.selectionStart;
            const end = this.selectionEnd;


            this.value =
                this.value.substring(0, start) +
                "    " +
                this.value.substring(end);


            this.selectionStart =
                this.selectionEnd =
                start + 4;

        }

    });


    /* ============================================================
       CTRL + ENTER TO SUBMIT
    ============================================================ */

    editor.addEventListener("keydown", function (event) {

        if (
            event.ctrlKey &&
            event.key === "Enter"
        ) {

            event.preventDefault();

            codeForm.requestSubmit();

        }

    });


    /* ============================================================
       SUBMIT BUTTON
    ============================================================ */

    codeForm.addEventListener("submit", function (event) {

        const code = editor.value.trim();


        /* EMPTY CODE CHECK */

        if (code === "") {

            event.preventDefault();

            alert(
                "🐻 Write some Python code first!"
            );

            editor.focus();

            return;

        }


        /* PREVENT DOUBLE CLICK */

        submitButton.disabled = true;

        submitButton.innerHTML =
            "⏳ Checking...";


        /* SAFETY:
           If something prevents navigation,
           restore the button after 10 seconds.
        */

        setTimeout(function () {

            if (submitButton.disabled) {

                submitButton.disabled = false;

                submitButton.innerHTML =
                    "▶ Run & Submit";

            }

        }, 10000);

    });

});