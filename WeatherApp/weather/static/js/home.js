const temperaturesForm = document.getElementById("temperatures-form");
const averageForm = document.getElementById("average-form");

temperaturesForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = temperaturesForm.querySelector("button");
    button.disabled = true;

    try {
        const response = await fetch(temperaturesForm.action, {
            method: "POST",
            body: new FormData(temperaturesForm),
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Could not retrieve weather data.");
        }

        if (data.api_error) {
            alert(data.api_error);
            return;
        }

        const tbody = document.getElementById("weather-table-body");
        tbody.replaceChildren();

        for (const weather of data.weather_data) {
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
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
});


averageForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const button = averageForm.querySelector("button");
    button.disabled = true;

    try {
        const response = await fetch(averageForm.action, {
            method: "POST",
            body: new FormData(averageForm),
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Could not calculate the average.");
        }

        if (data.api_error) {
            alert(data.api_error);
            return;
        }

        document.getElementById("average-value").textContent =
            data.average === null ? "No data yet" : `${data.average} °C`;

        document.getElementById("average-count").textContent =
            data.count;
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
});
