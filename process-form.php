<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Capture and sanitize form data
    $name = filter_input(INPUT_POST, 'name', FILTER_SANITIZE_STRING);
    $email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
    $message = filter_input(INPUT_POST, 'message', FILTER_SANITIZE_STRING);

    // Basic validation to check if fields are empty
    if (empty($name) || empty($email) || empty($message)) {
        echo "All fields are required.";
        exit();  // Exit the script
    }

    // Email processing
    $to = "JoshGinz@udel.edu";
    $subject = "New Contact Form Submission";
    $body = "Name: $name\nEmail: $email\nMessage: $message";

    // Send email and check for success
    if (mail($to, $subject, $body)) {
        // Redirect to a thank you page
        header("Location: ./thank-you.html");
        exit();  // Exit the script
    } else {
        echo "Failed to send message. Please try again later.";
        exit();  // Exit the script
    }
}
?>
