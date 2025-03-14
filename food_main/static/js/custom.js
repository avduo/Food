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

//Cart
$(document).ready(function(){
    // Add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        product_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if (response.status == 'login_required'){
                   swal(response.message, '', 'info', {
                    button: "Login",
                  }).then(function(){
                    window.location = '/login';
                   })
                }else if (response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+product_id).html(response.qty)

                    //subtotal, tax and Grand total
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total'],
                    )
                }
            }
        })
    })
    //Place the cart items on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        // console.log('Initial quantity for', this.id, ':', qty);
        $('#'+ the_id).html(qty)
    })

    //Remove cart items
    $('.remove_from_cart').on('click', function(e){
        e.preventDefault();

        product_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if (response.status == 'login_required'){
                    swal(response.message, '', 'info', {
                     button: "Login",
                   }).then(function(){
                     window.location = '/login';
                    })
                 }else if (response.status == 'Failed'){
                     swal(response.message, '', 'error')
                 }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+product_id).html(response.qty)

                    if (window.location.pathname == '/cart/'){
                        deleteCartItem(response.qty, cart_id);
                        checkEmptyCart()
                    }

                    //subtotal, tax and Grand total
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total'],
                    )
                }
            }
        })
    })
    // Delete cart items
    $('.delete_cart').on('click', function(e){
        e.preventDefault();

        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                // if (response.status == 'login_required'){
                //     swal(response.message, '', 'info', {
                //      button: "Login",
                //    }).then(function(){
                //      window.location = '/login';
                //     })
                //  }else
                 if (response.status == 'Failed'){
                     swal(response.message, '', 'error')
                 }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    swal(response.status, response.message, 'success')

                    deleteCartItem(0, cart_id);
                    checkEmptyCart()

                    //subtotal, tax and Grand total
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total'],
                    )

                }
            }
        })
    })
    // Delete Cart element if qty is 0
    function deleteCartItem(cartItemQty, cart_id){
        if (cartItemQty <= 0){
            // Remove the element
            document.getElementById("cart-item-"+cart_id).remove()
        }

    }
    //Check if cart is empty
    function checkEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if (cart_counter == 0){
            document.getElementById("empty-cart").style.display = "block";
        }
    }
    //Apply cart amounts
    function applyCartAmounts(subtotal, tax, grand_total){
        if (window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)
        }
    }

    //Add Shop Opening Hours
    $('.add_hours').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_day').value;
        var opening_time = document.getElementById('id_opening_time').value;
        var closing_time = document.getElementById('id_closing_time').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var cfrf_token = $('input[name="csrfmiddlewaretoken"]').val();
        var url = document.getElementById('add_hours_url').value;


        console.log(day, opening_time, closing_time, is_closed, cfrf_token)
        if (is_closed == true){
            condition = "day !=''"
        }else{
            condition = "day != '' && opening_time != '' && closing_time != ''"
        }
        if(eval(condition)){
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'opening_time': opening_time,
                    'closing_time': closing_time,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': cfrf_token
                },
                success: function(response){
                    console.log(response)
                    if(response.status == 'success'){
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</b></td><td><a href="#"><i class="text-primary fa-solid fa-pencil"></i></a></td><td><a href="#"><i class="text-danger delete_hours fa-solid fa-trash" data-url="/vendor/opening-hours/delete/'+response.id+'/"></i></a></td></tr>';
                        }else{
                        html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.opening_time+' - '+response.closing_time+'</td><td><a href="#"><i class="text-primary fa-solid fa-pencil"></i></a></td><td><a href="#"><i class="text-danger delete_hours fa-solid fa-trash"data-url="/vendor/opening-hours/delete/'+response.id+'/"></i></a></td></tr>';
                        }
                        $('.opening-hours').append(html);
                        document.getElementById("opening-hours").reset();
                        swal('You have updated your opening hours', '', 'success')
                    }else{
                        swal(response.message, '', 'error')
                    }

                }
            })
        }else{
            swal('Please fill all the fields','', 'info')
        }
    })
    
    //Delete Shop Opening Hours
    $(document).on('click', '.delete_hours', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        console.log(url);
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                    // $('.opening-hours').empty();
                    swal('You have deleted your opening hours', '', 'success')
                }else{
                    swal(response.message, '', 'error')
                }
            }
        })
    })
});