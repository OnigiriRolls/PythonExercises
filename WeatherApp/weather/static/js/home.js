const temperaturesForm = document.getElementById("temperatures-form");
const averageForm = document.getElementById("average-form");
const historyForm = document.getElementById("history-form");
const historyFilters = document.getElementById("history-filters");
const historyPagination = document.getElementById("history-pagination");

let currentPage = 1;
let totalPages = 1;

function showHistoryFiltersAndPaginationRow(show) {
    historyFilters.hidden = !show;
    historyPagination.hidden = !show;
}

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
        showHistoryFiltersAndPaginationRow(false);
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

function getHistoryFilters() {
    return {
        city: document.getElementById("filter-city").value.trim(),
        country: document.getElementById("filter-country").value.trim(),
        latitude: document.getElementById("filter-latitude").value.trim(),
        longitude: document.getElementById("filter-longitude").value.trim(),
        temperature_min: document.getElementById("filter-temperature-min").value.trim(),
        temperature_max: document.getElementById("filter-temperature-max").value.trim(),
        feels_like_min: document.getElementById("filter-feels-like-min").value.trim(),
        feels_like_max: document.getElementById("filter-feels-like-max").value.trim()
    };
}

async function loadHistory(page = 1) {
    const button = historyForm.querySelector("button");
    const errorElement = document.getElementById("location-error");
    button.disabled = true;
    errorElement.textContent = "";

    try {
        const formData = new FormData(historyForm);
        const filters = getHistoryFilters();
        for (const [key, value] of Object.entries(filters)) {
            formData.set(key, value);
        }
        formData.set("page", page);

        const response = await fetch(historyForm.action, {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        if (!response.ok) {
            if (data.errors) {
                const messages = Object.values(data.errors)
                    .flat()
                    .map(error => error.message);
                throw new Error(messages.join(" "));
            }
            throw new Error("Could not retrieve history.");
        }
        const errorElement = document.getElementById("history-error");
        if (data.api_error) {
            errorElement.textContent = Object.entries(data.api_error)
                .map(([field, errors]) =>
                    `${field}: ${errors.map(error => error.message).join(", ")}`
                )
                .join(" ");

            errorElement.hidden = false;
            return;
        }

        populateWeatherTable(data.weather_data);
        errorElement.hidden = true;
        showHistoryFiltersAndPaginationRow(true);
        currentPage = data.pagination.current_page;
        totalPages = data.pagination.total_pages;
        document.getElementById("page-info").textContent = `Page ${currentPage} of ${totalPages}`;
        document.getElementById("previous-page").disabled = !data.pagination.has_previous;
        document.getElementById("next-page").disabled = !data.pagination.has_next;
    } catch (error) {
        errorElement.textContent = error.message;
    } finally {
        button.disabled = false;
    }
}

historyForm.addEventListener("submit", function (event) {
    event.preventDefault();
    loadHistory(1);
});

document.getElementById("previous-page").addEventListener("click", function () {
    if (currentPage > 1) {
        loadHistory(currentPage - 1);
    }
});

document.getElementById("next-page").addEventListener("click", function () {
    if (currentPage < totalPages) {
        loadHistory(currentPage + 1);
    }
});

const historyFilterIds = [
    "filter-city",
    "filter-country",
    "filter-latitude",
    "filter-longitude",
    "filter-temperature-min",
    "filter-temperature-max",
    "filter-feels-like-min",
    "filter-feels-like-max"
];

for (const id of historyFilterIds) {
    document.getElementById(id).addEventListener("change", function () {
        loadHistory(1);
    });
}