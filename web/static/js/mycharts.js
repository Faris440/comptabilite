function script() {
  const ctx = document.getElementById("myChart1");
  draw_by_resident(ctx?.dataset.code);
  draw_by_payment(ctx?.dataset.code);
  draw_by_profile(ctx?.dataset.code);
  draw_by_validate(ctx?.dataset.code);
  draw_by_gender(ctx?.dataset.code);
  draw_by_date(ctx?.dataset.code);
}

function draw_by_resident(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-resident/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart1");
    const myChart1 = new Chart(ctx, {
      type: "bar",
      data: data,
      options: options,
    });
  });
}
function draw_by_payment(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-payment/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart2");
    const myChart2 = new Chart(ctx, {
      type: "pie",
      data: data,
      options: options,
    });
  });
}

function draw_by_profile(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-profile/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart3");
    const myChart3 = new Chart(ctx, {
      type: "pie",
      data: data,
      options: options,
    });
  });
}

function draw_by_validate(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-validate/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart4");
    const myChart4 = new Chart(ctx, {
      type: "pie",
      data: data,
      options: options,
    });
  });
}

function draw_by_gender(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-gender/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart5");
    const myChart4 = new Chart(ctx, {
      type: "pie",
      data: data,
      options: options,
    });
  });
}

function draw_by_date(code) {
  $.get(`/projects/operations/${code}/subscriptions/charts-by-date/`, function (response) {
    const {data, options} = response;
    const ctx = document.getElementById("myChart6");
    const myChart4 = new Chart(ctx, {
      type: "line",
      data: data,
      options: options,
    });
  });
}

$(document).ready(script);
