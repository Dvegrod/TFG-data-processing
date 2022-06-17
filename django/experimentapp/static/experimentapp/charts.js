
function displayLineChart(canvas_id, xdata, ydata) {
    new Chart("CHART-"+canvas_id, {
        type: line,
        data: {
            labels: xdata,
            datasets: ydata
        },
        options: {
            legend: {
                display: false
            }
        }
    })
}
