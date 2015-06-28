
$(function() {
    var currentName = "";

    function handleReceivedGenderDebugData(data) {
        console.log(data)
    }

    function updateCurrentNameFromInput() {
        name = $("#name-input").val()
        if (name && name.length > 1 && currentName != name) {
            currentName = name
            return true
        }
        return false
    }

    function buildFinalResultText(distLabel, dataLabel) {
        if (dataLabel != 2)
            return "I determined from a direct lookup in my database that \"" + currentName + "\" is a " + (dataLabel ? "feminine" : "masculine") + " name."

        if (distLabel != 2)
            return "My SVM predicts that \"" + currentName + "\" is probably a " + (distLabel ? "feminine" : "masculine") + " name. The name \"" + currentName + "\" is missing from my database."

        return "Hmm...we weren't really able to determine whether \"" + currentName + "\" is a masculine or feminine name."
    }

    function buildDistanceResultText(distance) {
        return "The name is " + distance + " units from the separating hyperplane.";
    }

    function update() {
        if (!updateCurrentNameFromInput())
            return;

        $.getJSON("http://gender-ml.herokuapp.com/debug?callback=?&name=" + currentName, null, function(data) {
            var distLabel = parseInt(data["label_from_dist"]);
            var dataLabel = parseInt(data["label_from_data"]);
            var distance = Math.round(parseFloat(data["hyperplane_dist"]) * 100) / 100;
            $("#result").text(buildFinalResultText(distLabel, dataLabel) + "  " + buildDistanceResultText(distance));
            var genderIcon = $("#gender-icon");
            genderIcon.show().removeClass();
            var prediction = dataLabel == 2 ? distLabel : dataLabel;
            if (prediction == 0)
                genderIcon.addClass("male");
            else if (prediction == 1)
                genderIcon.addClass("female");
            else
                genderIcon.addClass("neutral");
        });
    }

    setInterval(update, 1000);
});
