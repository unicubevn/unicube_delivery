-- disable momo payment provider
UPDATE payment_provider
   SET code = NULL,
       custom_mode = NULL,
       qr_code = NULL;
