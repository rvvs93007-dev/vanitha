async function postJSON(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "same-origin",
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Request failed."
        );
    }

    return data;
}


async function postForm(url, formData) {
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        body: formData
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.detail ||
            "Request failed."
        );
    }

    return data;
}


function money(value) {
    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(Number(value || 0));
}


function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}


function renderRecommendations(data, targetId) {
    const target = document.getElementById(targetId);

    if (!target) {
        return;
    }

    const recommendations =
        data.recommendations || [];

    const allocations =
        data.allocations || {};

    let html = `
        <div class="result-header">
            <span class="badge">
                ${escapeHtml(data.source || "AI")}
            </span>

            <h2>
                Recommendation Summary
            </h2>

            <p>
                ${escapeHtml(data.summary || "")}
            </p>

            <strong>
                Budget: ${money(data.budget)}
            </strong>

            <div class="allocation-list">
    `;

    for (const [key, value] of Object.entries(allocations)) {
        html += `
            <div class="allocation">
                <span>${escapeHtml(key)}</span>
                <strong>${money(value)}</strong>
            </div>
        `;
    }

    html += `
            </div>
        </div>

        <div class="recommendations">
    `;

    for (const item of recommendations) {
        html += `
            <article class="recommendation-card">
                <span class="badge">
                    ${escapeHtml(item.platform)}
                </span>

                <h3>
                    ${escapeHtml(item.title)}
                </h3>

                <div>
                    ${escapeHtml(item.category)}
                </div>

                <div class="price">
                    ${money(item.price)}
                </div>

                <p>
                    ${escapeHtml(item.reason)}
                </p>

                ${
                    item.url
                    ? `
                        <a
                            class="btn btn-secondary"
                            href="${escapeHtml(item.url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Search Product
                        </a>
                    `
                    : ""
                }
            </article>
        `;
    }

    html += `
        </div>
    `;

    if (data.notes?.length) {
        html += `
            <div class="result-header">
                <h3>Notes</h3>
                <ul>
                    ${data.notes.map(
                        note =>
                            `<li>${escapeHtml(note)}</li>`
                    ).join("")}
                </ul>
            </div>
        `;
    }

    target.innerHTML = html;
}


function setLoading(
    loadingId,
    enabled
) {
    const element =
        document.getElementById(loadingId);

    if (!element) {
        return;
    }

    element.classList.toggle(
        "active",
        enabled
    );
}


function showError(
    targetId,
    message
) {
    const target =
        document.getElementById(targetId);

    if (!target) {
        return;
    }

    target.innerHTML = `
        <div class="alert alert-error">
            ${escapeHtml(message)}
        </div>
    `;
}


async function submitHomeForm(event) {
    event.preventDefault();

    setLoading("home-loading", true);

    try {
        const form =
            event.target;

        const rooms = [
            ...form.querySelectorAll(
                'input[name="rooms"]:checked'
            )
        ].map(
            input => input.value
        );

        const items = [
            {
                category: "Lights",
                quantity: Number(
                    form.lights.value || 0
                )
            },
            {
                category: "Ceiling Fans",
                quantity: Number(
                    form.fans.value || 0
                )
            },
            {
                category: "Dining Table",
                quantity: Number(
                    form.dining_table.value || 0
                )
            },
            {
                category: "Sofa",
                quantity: Number(
                    form.sofa.value || 0
                )
            }
        ].filter(
            item => item.quantity > 0
        );

        const payload = {
            budget: Number(
                form.budget.value
            ),
            rooms,
            style: form.style.value,
            items,
            city: form.city.value || null
        };

        const data =
            await postJSON(
                "/api/generate-home",
                payload
            );

        renderRecommendations(
            data,
            "home-result"
        );

    } catch (error) {
        showError(
            "home-result",
            error.message
        );
    } finally {
        setLoading(
            "home-loading",
            false
        );
    }
}


async function submitPartyForm(event) {
    event.preventDefault();

    setLoading(
        "party-loading",
        true
    );

    try {
        const form =
            event.target;

        const payload = {
            budget: Number(
                form.budget.value
            ),
            guests: Number(
                form.guests.value
            ),
            event_type:
                form.event_type.value,
            venue_type:
                form.venue_type.value,
            city:
                form.city.value || null,
            food_preference:
                form.food_preference.value ||
                null,
            decoration_style:
                form.decoration_style.value ||
                null
        };

        const data =
            await postJSON(
                "/api/generate-party",
                payload
            );

        renderRecommendations(
            data,
            "party-result"
        );

    } catch (error) {
        showError(
            "party-result",
            error.message
        );
    } finally {
        setLoading(
            "party-loading",
            false
        );
    }
}


async function submitJewelryForm(event) {
    event.preventDefault();

    setLoading(
        "jewelry-loading",
        true
    );

    try {
        const form =
            event.target;

        const formData =
            new FormData(form);

        const data =
            await postForm(
                "/api/generate-jewelry",
                formData
            );

        renderRecommendations(
            data,
            "jewelry-result"
        );

    } catch (error) {
        showError(
            "jewelry-result",
            error.message
        );
    } finally {
        setLoading(
            "jewelry-loading",
            false
        );
    }
}


async function submitAuthForm(
    event,
    endpoint
) {
    event.preventDefault();

    const form =
        event.target;

    const formData =
        new FormData(form);

    try {
        const response =
            await postForm(
                endpoint,
                formData
            );

        if (response.success) {
            window.location.href =
                "/dashboard";
        }
    } catch (error) {
        const target =
            document.getElementById(
                "auth-error"
            );

        if (target) {
            target.innerHTML = `
                <div class="alert alert-error">
                    ${escapeHtml(error.message)}
                </div>
            `;
        }
    }
}


async function logout() {
    try {
        await fetch(
            "/api/auth/logout",
            {
                method: "POST",
                credentials: "same-origin"
            }
        );
    } finally {
        window.location.href = "/";
    }
}