async function api(
  url,
  options = {}
) {

  const response = await fetch(
    url,
    {
      credentials: "include",
      ...options,
    }
  );

  const data =
    await response
      .json()
      .catch(() => ({}));

  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Something went wrong."
    );
  }

  return data;
}


function showMessage(
  text,
  ok = false
) {

  const el =
    document.querySelector(
      "#form-message"
    );

  if (el) {

    el.textContent = text;

    el.style.color =
      ok
        ? "#027a48"
        : "#b42318";
  }
}


async function setupAuth() {

  const login =
    document.querySelector(
      "#login-form"
    );

  const register =
    document.querySelector(
      "#register-form"
    );


  if (login) {

    login.addEventListener(
      "submit",
      async (e) => {

        e.preventDefault();

        const body =
          Object.fromEntries(
            new FormData(
              login
            ).entries()
          );

        try {

          await api(
            "/api/auth/login",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body:
                JSON.stringify(body),
            }
          );

          location.href =
            "/dashboard";

        } catch (err) {

          showMessage(
            err.message
          );
        }
      }
    );
  }


  if (register) {

    register.addEventListener(
      "submit",
      async (e) => {

        e.preventDefault();

        const body =
          Object.fromEntries(
            new FormData(
              register
            ).entries()
          );

        try {

          await api(
            "/api/auth/register",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body:
                JSON.stringify(body),
            }
          );

          location.href =
            "/dashboard";

        } catch (err) {

          showMessage(
            err.message
          );
        }
      }
    );
  }
}


function money(value) {

  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",

      currency: "INR",

      maximumFractionDigits: 0,
    }
  ).format(value);
}


function renderResult(
  result
) {

  const el =
    document.querySelector(
      "#result"
    );

  if (!el) return;


  const allocations =
    Object.entries(
      result.allocation || {}
    )

      .map(
        ([key, value]) => `

          <div
            class="allocation-item"
          >

            <span>
              ${escapeHtml(key)}
            </span>

            <strong>
              ${money(value)}
            </strong>

          </div>

        `
      )

      .join("");


  const cards =
    (
      result.recommendations || []
    )

      .map(
        item => `

          <article
            class="recommendation"
          >

            <span class="badge">
              ${escapeHtml(
                item.category
              )}
            </span>

            <h4>
              ${escapeHtml(
                item.title
              )}
            </h4>

            <div class="price">
              ${money(item.price)}
            </div>

            <div class="platform">

              ${escapeHtml(
                item.platform
              )}

              ·

              ${Number(
                item.budget_share
              ).toFixed(1)}%

              of budget

            </div>

            <p>
              ${escapeHtml(
                item.reason
              )}
            </p>

            <a
              class="button ghost"
              target="_blank"
              rel="noopener"
              href="${escapeAttr(
                item.url
              )}"
            >
              Search option →
            </a>

          </article>

        `
      )

      .join("");


  el.classList.remove(
    "empty"
  );


  el.innerHTML = `

    <div class="result-header">

      <div>

        <span class="badge">

          ${escapeHtml(
            result.source
          )}
          mode

        </span>

        <h2>
          Your plan
        </h2>

      </div>

      <strong>
        ${money(result.budget)}
      </strong>

    </div>


    <p>
      ${escapeHtml(
        result.summary
      )}
    </p>


    ${
      result.image_insight

        ? `

          <div
            class="history-item"
          >

            <strong>
              Image insight
            </strong>

            <p>
              ${escapeHtml(
                result.image_insight
              )}
            </p>

          </div>

        `

        : ""
    }


    <h3>
      Budget allocation
    </h3>


    <div
      class="allocation-grid"
    >
      ${allocations}
    </div>


    <h3>
      Recommendations
    </h3>


    <div
      class="recommendations"
    >

      ${
        cards ||
        "<p>No matching catalog entries were found.</p>"
      }

    </div>

  `;
}


function escapeHtml(
  value
) {

  return String(
    value ?? ""
  ).replace(
    /[&<>"']/g,

    ch =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[ch]
  );
}


function escapeAttr(
  value
) {

  return escapeHtml(
    value
  ).replace(
    /javascript:/gi,
    ""
  );
}


async function setupPlanner() {

  const form =
    document.querySelector(
      "#planner-form"
    );

  if (!form) return;


  form.addEventListener(
    "submit",
    async (e) => {

      e.preventDefault();

      showMessage(
        "Generating…",
        true
      );


      try {

        const planner =
          form.dataset.planner;

        let body;

        let headers = {};

        let endpoint =
          `/api/generate-${planner}`;


        if (
          planner === "jewelry"
        ) {

          body =
            new FormData(
              form
            );

        } else {

          const fd =
            new FormData(
              form
            );

          const raw =
            Object.fromEntries(
              fd.entries()
            );


          if (
            planner === "home"
          ) {

            raw.budget =
              Number(
                raw.budget
              );

            raw.occupants =
              Number(
                raw.occupants || 1
              );

            raw.items =
              raw.items
                ? raw.items
                    .split(",")
                    .map(
                      x =>
                        x.trim()
                    )
                    .filter(Boolean)

                : [];

            raw.priorities =
              raw.priorities
                ? raw.priorities
                    .split(",")
                    .map(
                      x =>
                        x.trim()
                    )
                    .filter(Boolean)

                : [];

          } else {

            raw.budget =
              Number(
                raw.budget
              );

            raw.guests =
              Number(
                raw.guests
              );
          }


          body =
            JSON.stringify(
              raw
            );

          headers[
            "Content-Type"
          ] =
            "application/json";
        }


        const result =
          await api(
            endpoint,
            {
              method: "POST",

              headers,

              body,
            }
          );


        renderResult(
          result
        );


        showMessage(
          "Plan generated successfully.",
          true
        );

      } catch (err) {

        showMessage(
          err.message
        );
      }
    }
  );
}


async function loadUserAndHistory() {

  const welcome =
    document.querySelector(
      "#welcome"
    );

  const recent =
    document.querySelector(
      "#recent-history"
    );

  const history =
    document.querySelector(
      "#history-list"
    );


  try {

    const me =
      await api(
        "/api/auth/me"
      );

    if (welcome) {

      welcome.textContent =
        `Hi, ${me.name}`;
    }

  } catch {

    if (welcome) {

      welcome.textContent =
        "Please log in";
    }
  }


  if (
    !recent &&
    !history
  ) {

    return;
  }


  try {

    const rows =
      await api(
        "/api/history?limit=20"
      );


    if (history) {

      history.innerHTML =
        rows
          .map(historyCard)
          .join("") ||

        "<p>No recommendations yet.</p>";
    }


    if (recent) {

      recent.innerHTML =
        rows
          .slice(0, 3)
          .map(historyCard)
          .join("") ||

        "<p>No recommendations yet.</p>";
    }

  } catch (err) {

    if (history) {

      history.innerHTML =
        `<p>${escapeHtml(
          err.message
        )}</p>`;
    }

    if (recent) {

      recent.innerHTML =
        `<p>${escapeHtml(
          err.message
        )}</p>`;
    }
  }
}


function historyCard(
  row
) {

  const date =
    new Date(
      row.created_at
    ).toLocaleString();


  return `

    <article
      class="history-item"
    >

      <header>

        <strong>
          ${escapeHtml(
            row.planner_type
              .toUpperCase()
          )}
        </strong>

        <span>
          ${escapeHtml(
            date
          )}
        </span>

      </header>


      <p>
        ${escapeHtml(
          row.result?.summary || ""
        )}
      </p>


      <a
        href="/planner/${escapeAttr(
          row.planner_type
        )}"
      >
        Create another →
      </a>

    </article>

  `;
}


async function setupLogout() {

  const btn =
    document.querySelector(
      "#logout-btn"
    );

  if (!btn) return;


  btn.addEventListener(
    "click",
    async () => {

      await api(
        "/api/auth/logout",
        {
          method: "POST"
        }
      );

      location.href =
        "/login";
    }
  );
}


document.addEventListener(
  "DOMContentLoaded",
  () => {

    setupAuth();

    setupPlanner();

    loadUserAndHistory();

    setupLogout();

  }
);