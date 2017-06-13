/**
 * Created by jc225327 on 11/06/2017.
 */

let sort_by = function(field, reverse, primer){

    let key = primer ?
        function(x) {return primer(x[field])} :
        function(x) {return x[field]};

    reverse = !reverse ? 1 : -1;

    return function (a, b) {
        return a = key(a), b = key(b), reverse * ((a > b) - (b > a));
    }
};

let attach_tooltip = function(meta, config, colours, K){

    // Returns meta list with tooltips attached for
    // the selected K

    for(let i = 0; i < meta.length; i++) {

        let text = "<span style='font-weight:bold'>Sample:</span><br><br>";

        text += "<span style='font-weight:bold'>ID</span>: " + meta[i].id + "<br>";
        text += "<span style='font-weight:bold'>Pop</span>: " + meta[i].pop + "<br><br>";
        text += "<span style='font-weight:bold'>Admixture:</span><br><br>";

        for(let j = 0; j < K; j++){
            let k_value = meta[i].K[K.toString()][j];

            text += "<span style='color:" + colours[j] + ";font-weight:bold'>K" + (j+1) + "</span>: " + k_value + "<br>"

        }

        meta[i].tooltip = text
    }

    return meta

};

let attach_infobox = function(meta){

    for(let i = 0; i < meta.length; i++) {
        let text = "";

        if(meta[i].image){

            text = '<div class=thumbnail style="background-image: url(' + meta[i].image + ');"></div>';

            text += "<h1>" + meta[i].info.title + "</h1><br><br>"
        } else{
            text = "<h1>" + meta[i].info.title + "</h1><br><br>";
        }

        text += meta[i].info.text + "<br>";

        meta[i].infobox = text
    }

    return meta
};
