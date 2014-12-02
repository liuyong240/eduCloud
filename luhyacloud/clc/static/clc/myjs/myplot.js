//Flot Moving Line Chart



function draw_plot(idstring, url) {

    var container = $(idstring);

    // Determine how many data points to keep based on the placeholder's initial size;
    // this gives us a nice high-res plot while avoiding more than one point per pixel.

    var maximum = container.outerWidth() / 2 || 300;

    //

    var data = [];
    var cache_data = [];
    var flag = 0;

    function retriveData() {
        $.getJSON(url,function (data) {
            var items = [];
            $.each(data, function (key, val) {
                items[key] = val;
            });
            $.merge(cache_data, items['value']);;
            flag = 0;
        });

    }

    function init_data() {
        while (data.length < maximum) {
            data.push(0);
        }

        setTimeout(retriveData, 40);

        var res = [];
        for (var i = 0; i < data.length; ++i) {
            res.push([i, data[i]])
        }

        return res;
    }

    function getRandomData() {
        if (data.length) {
            data = data.slice(1);
        }

        //console.log( "before:" + data.length );
        //console.log( "before:" + cache_data.length);
        while (data.length < maximum) {

            if (cache_data.length == 0) {
                data.push(0);
                if (flag == 0) {
                    //console.log("retriveData() is callled when cache_data.length = 0... ...");
                    setTimeout(retriveData, 40);
                    flag = 1;
                }
            } else if (cache_data.length < 200 ) {
                if (flag == 0) {
                    //console.log("retriveData() is callled ... ...");
                    setTimeout(retriveData, 40);
                    flag = 1;
                }
                data.push(cache_data[0]);
                cache_data = cache_data.slice(1);
            } else {
                data.push(cache_data[0]);
                cache_data = cache_data.slice(1);
            }
        }
        //console.log( "after:" + data.length );
        //console.log( "after:" + cache_data.length);

        // zip the generated y values with the x values

        var res = [];
        for (var i = 0; i < data.length; ++i) {
            res.push([i, data[i]])
        }

        return res;
    }

    //

    series = [{
        data: init_data(),
        lines: {
            fill: true
        }
    }];

    //

    var plot = $.plot(container, series, {
        grid: {
            borderWidth: 1,
            minBorderMargin: 20,
            labelMargin: 10,
            backgroundColor: {
                colors: ["#fff", "#e4f4f4"]
            },
            margin: {
                top: 8,
                bottom: 20,
                left: 20
            },
            markings: function(axes) {
                var markings = [];
                var xaxis = axes.xaxis;
                for (var x = Math.floor(xaxis.min); x < xaxis.max; x += xaxis.tickSize * 2) {
                    markings.push({
                        xaxis: {
                            from: x,
                            to: x + xaxis.tickSize
                        },
                        color: "rgba(232, 232, 255, 0.2)"
                    });
                }
                return markings;
            }
        },
        xaxis: {
            tickFormatter: function() {
                return "";
            }
        },
        yaxis: {
            min: 0,
            max: 110
        },
        legend: {
            show: true
        }
    });

    // Update the random dataset at 25FPS for a smoothly-animating chart

    function updateRandom() {
        series[0].data = getRandomData();
        plot.setData(series);
        plot.draw();
        if (cache_data.length == 0) {
            inteval = 5000;
        } else {
            inteval = 100;
        }
        setTimeout(updateRandom, inteval);
    }

    setTimeout(updateRandom, 500);
}
