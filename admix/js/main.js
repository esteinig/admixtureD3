/**
 * Created by jc225327 on 10/06/2017.
 */


// Interface Configuration

let width = 600;
let height = 400;

let left_info_margin = 50;
let top_info_margin = 50;
let bottom_plot_margin = 20;
let bottom_opt_margin = 10;
let info_width = 100;
let left_plot_margin = 200;
let top_plot_margin = 50;

let sorts = {
    "Population": "pop",
    "Sample ID": "id",
    "Admixture": "K"
};


let sort_values = ["Population", "Sample ID", "Admixture"];

d3.json("data.json", function(error, data) {
    let meta = data["samples"];
    let config = data["config"];

// A dictionary with sorting names (appear in plot) and
// keys in meta data to sort by.

// Select admixture K

    let selectK = Math.min(...config.K);
    let sort_index = 0; // Sorted by Population

// Get admixture K colours and tooltips:

    let colours = d3["scheme" + config.palette];

// Main Body

    let chart = d3.select("body")
        .append("svg")
        .attr("id", "Main")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", function () {
            chart.attr("transform", d3.event.transform)
        }))
        .append("g")
        .attr("id", "AdmixtureGraph");

// Tooltips CSS

    let tooltip = d3.select("body").append("div")
        .attr("class", "hidden tooltip");

    let info = d3.select("body").append("div")
        .attr("class", "hidden info")
        .attr("style", 'left:' + left_info_margin + "px; top:" + top_info_margin +
            "px; width:" + info_width + "px");

// Block Shell
    let admixShell = chart.append("g")
        .attr("id", "SampleShell");

    let propShell = admixShell.append("g")
        .attr("id", "ProportionShell");

    let optShell = chart.append("g")
        .attr("id", "OptionShell");

// Option Selectors

    let option_x = 0;
    let option_align = "start";

    if (config.option_align === "center"){
        console.log("Setting options to center of Admixture Plot");
        option_x = (config.bar_width*meta.length)/2;
        option_align = "middle";
    }

    optShell.append("text")
        .attr("id", "selectK")
        .attr("class", "selectText")
        .attr("x", left_plot_margin + option_x)
        .attr("y", top_plot_margin + config.bar_height + bottom_plot_margin)
        .style("opacity", 0.7)
        .style("text-anchor", option_align)
        .text("K" + selectK)
        .on("mouseover", function(){
            d3.select(this).style("opacity", 1)
        })
        .on("mouseout", function(){
            d3.select(this).style("opacity", 0.7)
        })
        .on("click", function(){
            next_k(this, true)
        })
        .on("contextmenu", function() {
            d3.event.preventDefault();
            next_k(this, false)
        });

    optShell.append("text")
        .attr("id", "selectOrder")
        .attr("class", "selectText")
        .attr("x", left_plot_margin + option_x)
        .attr("y", top_plot_margin + config.bar_height + bottom_plot_margin + bottom_opt_margin)
        .style("opacity", 0.7)
        .style("text-anchor", option_align)
        .text(sort_values[sort_index])
        .on("mouseover", function(){
            d3.select(this).style("opacity", 1)
        })
        .on("mouseout", function(){
            d3.select(this).style("opacity", 0.7)
        })
        .on("click", function(){
            sort_plot_next(this);
        })
        .on("contextmenu", function() {
            d3.event.preventDefault();
            sort_plot_previous(this);
        });

    let next_k = function(k_text, next=false){

        // Move through K

        if (next){
            selectK += 1;
        } else {
            selectK -= 1;
        }

        if (selectK < Math.min(...config.K)){
            selectK = Math.max(...config.K)
        }

        if (selectK > Math.max(...config.K)){
            selectK = Math.min(...config.K)
        }

        d3.select(k_text).text("K" + selectK);
        propShell.remove();
        admixShell.remove();
        meta = attach_tooltip(meta, config, colours, selectK);
        draw_plot(meta, colours, selectK, sorts[sort_values[sort_index]], false)
    };

    let sort_plot_previous = function(sort_text){

        // Move to previous sort option

        sort_index -= 1;
        if (sort_index < 0) {
            sort_index = sort_values.length-1;
        }
        d3.select(sort_text).text(sort_values[sort_index]);
        redraw_plot()
    };

    let sort_plot_next = function(sort_text){

        // Move to next sort option

        console.log("Clicked sort plot next.");
        sort_index += 1;
        if (sort_index > sort_values.length-1) {
            sort_index = 0;
        }
        d3.select(sort_text).text(sort_values[sort_index]);
        redraw_plot()
    };

    let redraw_plot = function(){

        // Redraw the Admixture Plot

        propShell.remove();
        admixShell.remove();
        draw_plot(meta, colours, selectK, sorts[sort_values[sort_index]], false, colours)
    };

    let draw_plot = function(meta, colours, K, sort_key="pop", initial=false){

        // Attach current tooltips and infoboxes to meta data and
        // draw the Admixture Plot

        meta = attach_tooltip(meta, config, colours, selectK);
        meta = attach_infobox(meta);

        let order = sort_by(sort_key, false, function(x){ return x; });
        meta.sort(order);

        if (!initial) {

            admixShell = chart.append("g")
                .attr("id", "SampleShell");

            propShell = admixShell.append("g")
                .attr("id", "ProportionShell");
        }

        admixShell.selectAll("rect")
            .data(meta)
            .enter()
            .append("rect")
            .attr("id", function(d) { return d.id; })
            .attr("class", "admixtureBar")
            .attr("x", function(d, i){ return left_plot_margin + config.bar_width*i; })
            .attr("y", top_plot_margin)
            .attr("width", config.bar_width)
            .attr("height", config.bar_height)
            .style("stroke-opacity", 0.5)
            .style("fill-opacity", 0)
            .on("mouseover", function(d){
                d3.select(this).style("stroke-opacity", 1);
                tooltip.classed('hidden', false)
                    .attr('style', 'left:' + (d3.event.pageX + 20) + 'px; top:' + (d3.event.pageY - 20) + 'px')
                    .html(d.tooltip);
                info.classed('hidden', false)
                    .html(d.infobox);
            })
            .on("mouseout", function() {
                d3.select(this).style("stroke-opacity", 0.5);
                tooltip.classed('hidden', true);
                info.classed('hidden', true);
            });

        propShell.selectAll("g")
            .data(meta)
            .enter()
            .append("g")
            .attr("id", function (d) { return "adm_" + d.id} )
            .each(function(d, i) {
                let y_start = 0;
                for(let j = 0; j < d.K[selectK.toString()].length; j++) {
                    d3.select(this).append('rect')
                        .attr("class", "proportionBar K" + j)
                        .attr("x", left_plot_margin + config.bar_width*i)
                        .attr("y", top_plot_margin + y_start)
                        .attr("width", function(){ return config.bar_width; })
                        .attr("height", config.bar_height*d.K[selectK.toString()][j])
                        .style("fill", colours[j] )
                        .style("stroke-opacity", 0);

                    // this computes start of proportion bar on y-axis
                    // of nested admixture proportion rect inside view ports
                    // d.K[selectK] is the string K entry of each id in meta data, j is value of K
                    y_start = y_start + config.bar_height*d.K[selectK.toString()][j];
                }
            });

    };

// Initial Admixture Plot upon loading...

    draw_plot(meta, colours, selectK, "pop", true);

});

