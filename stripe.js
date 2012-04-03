$(document).ready(function(){
  Stripe.setPublishableKey('pk_oxUXr9EPxPOsfLcCJPRILvknGRVXU');

  function stripeResponseHandler(status, response){
    if(status === 200){
      console.log(response['id']);
      $("#id_stripe_token").val(response['id']);
      $("#stripe-payment-form").get(0).submit();
    } else {
      $("#stripe_error").append(response.error.message);
      $('input[type=submit]').attr('disabled', false);
    }
  }

  $("#stripe-payment-form").submit(function(event){
    $('input[type=submit]').attr("disabled", true);

    if($("#id_credit_number").length){
      Stripe.createToken({
        number: $('#id_credit_number').val(),
        cvc: $('#id_ccv').val(),
        exp_month: $('#id_month_expires').val(),
        exp_year: $('#id_year_expires').val()
      }, stripeResponseHandler);
      return false;
    } else {
      return false;
    }
  });
});
