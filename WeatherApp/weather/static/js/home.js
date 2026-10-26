const temperaturesForm = document.getElementById("temperatures-form");
const averageForm = document.getElementById("average-form");
const historyForm = document.getElementById("history-form");

function getLocationInputs() {
    const city = document.getElementById("city").value.trim();
    const latitude = document.getElementById("latitude").value.trim();
    const longitude = document.getElementById("longitude").value.trim();
    const errorElement = document.getElementById("location-error");
    errorElement.textContent = "";

    if (!latitude && !longitude) {
        if (!city) {
            errorElement.textContent = "Enter a city or both coordinates.";
            return null;
        }
        return { city, latitude: "", longitude: "" };
    }

    if (!latitude || !longitude) {
        errorElement.textContent = "Enter both latitude and longitude.";
        return null;
    }

    const decimalPattern = /^-?\d+(\.\d{1,2})?$/;
    if (!decimalPattern.test(latitude) || !decimalPattern.test(longitude)) {
        errorElement.textContent = "Coordinates can have at most 2 decimal places.";
        return null;
    }

    const lat = Number(latitude);
    const lon = Number(longitude);
    if (lat < -90 || lat > 90) {
        errorElement.textContent = "Latitude must be between -90 and 90.";
        return null;
    }
    if (lon < -180 || lon > 180) {
        errorElement.textContent = "Longitude must be between -180 and 180.";
        return null;
    }

    return { city, latitude, longitude };
}

function createLocationFormData(form) {
    const location = getLocationInputs();
    if (!location) return null;

    const formData = new FormData(form);
    formData.set("city", location.city);
    formData.set("latitude", location.latitude);
    formData.set("longitude", location.longitude);
    return formData;
}

function populateWeatherTable(weatherData) {
    const tbody = document.getElementById("weather-table-body");
    tbody.replaceChildren();
    for (const weather of weatherData) {
        const row = document.createElement("tr");
        const values = [
            weather.city_name,
            weather.country_code,
            weather.lat,
            weather.lon,
            weather.temp,
            weather.app_temp
        ];
        for (const value of values) {
            const cell = document.createElement("td");
            cell.textContent = value ?? "";
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }
}

temperaturesForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = temperaturesForm.querySelector("button");
    button.disabled = true;
    try {
        const formData = createLocationFormData(temperaturesForm);
        if (!formData) return;

        const response = await fetch(temperaturesForm.action, {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error("Could not retrieve weather data.");
        }
        if (data.api_error) {
            document.getElementById("location-error").textContent = data.api_error;
            return;
        }
        populateWeatherTable(data.weather_data);
    } catch (error) {
        document.getElementById("location-error").textContent = error.message;
    } finally {
        button.disabled = false;
    }
});


averageForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = averageForm.querySelector("button");
    button.disabled = true;

    try {
        const formData = createLocationFormData(averageForm);
        if (!formData) return;

        const response = await fetch(averageForm.action, {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error("Could not calculate the average.");
        }
        if (data.api_error) {
            document.getElementById("location-error").textContent = data.api_error;
            return;
        }

        document.getElementById("average-value").textContent = data.average === null ? "No data yet" : `${data.average} °C`;
        document.getElementById("average-count").textContent = data.count;
    } catch (error) {
        document.getElementById("location-error").textContent = error.message;
    } finally {
        button.disabled = false;
    }
});

historyForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = historyForm.querySelector("button");
    const errorElement = document.getElementById("location-error");
    button.disabled = true;
    errorElement.textContent = "";
    try {
        const response = await fetch(historyForm.action, {
            method: "POST",
            body: new FormData(historyForm),
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error("Could not retrieve history.");
        }
        if (data.api_error) {
            errorElement.textContent = data.api_error;
            return;
        }

        populateWeatherTable(data.weather_data);
    } catch (error) {
        errorElement.textContent = error.message;
    } finally {
        button.disabled = false;
    }
});