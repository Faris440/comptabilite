$(document).ready(function () {
  getlinechart();
  getbarchart();
  getpiechart();
  getradarchart();
  getpolarareachart();
  getdonutchart();
});



function getbarchart() {
  // Bar chart
  new Chart(document.getElementById("chartjs_bar"), {
    type: "bar",
    data: {
      labels: ["1ere classe", "2eme classe", "caporal", "sergent", "lieutenant"],
      datasets: [
        {
          label: "Nombres (mille)",
          backgroundColor: [
            "#3e95cd",
            "#8e5ea2",
            "#3cba9f",
            "#e8c3b9",
            "#c45850",
          ],
          data: [2478, 5267, 1734, 2548, 1433],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "#9aa0ac",
          },
        },
      },
      scales: { 
        x: {
          ticks: {
            color: "#9aa0ac",
          },
        },
        y: {
          ticks: {
            color: "#9aa0ac",
          },
        },
      },
    },
  });
}



function getdonutchart() {
  new Chart(document.getElementById("chartjs_donut"), {
    type: "doughnut",
    data: {
      labels: ["sous officier", "soldat", "officiers", "Offichier superieur"],
      datasets: [
        {
          label: "Nombre (mille)",
          backgroundColor: [
            "#3e95cd",
            "#8e5ea2",
            "#3cba9f",
            "#e8c3b9",
            "#c45850",
          ],
          data: [2478, 5267, 734, 784],
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Predicted world population (millions) in 2050",
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "#9aa0ac",
          },
        },
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}