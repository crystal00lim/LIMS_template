document.addEventListener('DOMContentLoaded', function() {
    const script = document.getElementById('parPie');
    console.log(script);
    const data = JSON.parse(script.textContent);

    const series = data.series;
    const labels = data.label;
    const title = data.title;

    const clean_series = series.filter(item => item != 0);
    const clean_labels = labels.filter(item => item != null);

    var pieChart = new ApexCharts(
        document.querySelector("#pieChart"), {
            chart: {
                type: 'pie',
                toolbar: {
                    show: true
                }
            },
            title: {text: title, align: 'center'},
            series: clean_series,
            labels: clean_labels,
            responsive: [{
                breakpoint: 480
            }],
            
        }
    );
    pieChart.render();
})