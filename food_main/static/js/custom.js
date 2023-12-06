// Vendor Auto add Address

let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['fr']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    // console.log(place)
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    // console.log(address)
    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results=>', results)
        // console.log('status=>', status)
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            // console.log('lat=>', latitude)
            // console.log('long=>', longitude)
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });
    console.log(place.address_components)
    // Loop through the address components and assign all address data.
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // Get Country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // Get state
            if(place.address_components[i].types[j] == 'administrative_area_level_2'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // Get City
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // Get Post code
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_post_code').val(place.address_components[i].long_name);
            }else{
                $('#id_post_code').val("");
            }

        }
    }
}

// Add to Cart
$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        product_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        data = {
            product_id:product_id,
        }

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(response){
                console.log(response)
            }
        })
    })
    //Place the cart item quantityon load
    console.log('Before each loop');
    // $('.item_qty').each(function(){
    //     var the_id = $(this).attr('id')
    //     var qty = $(this).attr('data-qty')
    //     console.log('Initial quantity for', this.id, ':', qty);
    //     $('#' + the_id).html(qty)
    // })

    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        console.log('Initial quantity for', this.id, ':', qty);
        $('#'+the_id).html(qty)
    })

    // $(document).ready(function(){
    //     // Place the cart item quantity on load
    //     $('.item_qty').each(function(){
    //         var qty = $(this).text();
    //         console.log('Initial quantity for', this.id, ':', qty);
    //         $(this).html(qty);
    //     });
    // });

});