document.getElementById('add-date-picker').valueAsDate = new Date();

// function to set chart mode
function setChartMode(metric) {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            const dates = data.dates;
            let values;
            let seriesName;
            let lineColor;
            let dotColor;

            // determine which dataset to use 
            if (metric === 'body_weight') {
                values = data.body_weight;
                seriesName = 'Body Weight';
                lineColor = '#007bff';  // blue color for body weight line
                dotColor = '#007bff';   // blue color for dots
            } else if (metric === 'muscle_weight') {
                values = data.muscle_weight;
                seriesName = 'Muscle Weight';
                lineColor = '#28a745';  // green color for muscle weight line
                dotColor = '#28a745';   // green color for dots
            } else if (metric === 'fat_weight') {
                values = data.fat_weight;
                seriesName = 'Fat Weight';
                lineColor = '#dc3545';  // red color for fat weight line
                dotColor = '#dc3545';   // red color for dots
            }

            // initialize the chart
            let chartDom = document.getElementById('chart');
            let myChart = echarts.init(chartDom);

            // chart options
            let option = {
                title: {
                    text: seriesName + ' Over Time'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: dates
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                        name: seriesName,
                        data: values,
                        type: 'line',
                        smooth: true,
                        lineStyle: {
                            color: lineColor,  // set line color
                            width: 3  // set line width
                        },
                        itemStyle: {
                            color: dotColor,  // set dots color 
                            borderColor: '#fff',  // border color for dots
                            borderWidth: 2  // set border width
                        },
                        emphasis: {
                            itemStyle: {
                                color: dotColor,  // change circle color in the tooltip
                                borderColor: '#000',  // set border color on hover
                                borderWidth: 3  // set border width on hover
                            }
                        },
                        symbol: 'circle',   // change shape of the dots
                        symbolSize: 8       // size of the dots
                    }
                ]
            };

            // set the options to the chart instance
            myChart.setOption(option);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// load default data on the page load
document.addEventListener('DOMContentLoaded', function() {
    setChartMode('body_weight');  // default chart is body weight
});
