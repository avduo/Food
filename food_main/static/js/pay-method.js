function payMethodConfirm(){
    var payMethod = $ ("input[name='payment-method']:checked").val();
    if(!payMethod){
        $('#payment-method-error').html("Please select a payment method!")
        return false;
    }else{
        var conf = confirm('You have selected ' + payMethod + ' as your payment method. \nClick "OK" to continue.');
        if(conf == true){
            return true;
        }else{
            return false;
        }
    }
}

$(function() {
    $('input[name="payment-method"]').change(function() {
      $('#payment-method-error').html('');
    });
  });