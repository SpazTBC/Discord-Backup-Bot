<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        .container {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .status {
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 8px;
            background-color: #e6f7e9; /* Green color for completed */
        }
        .status.pending {
            background-color: #fff3e0; /* Orange color for pending */
        }
        .user-list {
            list-style-type: none;
            padding: 0;
        }
        .user-list li {
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard</h1>
        </div>
        <?php
        // Function to fetch data from the API
        function fetch_data_from_api($url) {
            $response = file_get_contents($url);
            return json_decode($response, true);
        }

        // API endpoints
        $backup_count_url = "http://localhost:5000/api/backup/count";
        $user_count_url = "http://localhost:5000/api/user/count";
        $user_list_url = "http://localhost:5000/api/user/list";

        // Fetch data from API
        $backup_count = fetch_data_from_api($backup_count_url);
        $user_count = fetch_data_from_api($user_count_url);
        $user_list = fetch_data_from_api($user_list_url);
        ?>
<div id="statusContainer">
    <?php
    // Fetch initial backup status
    $initial_backup_status = fetch_data_from_api("http://localhost:5000/api/backup/status");
    // Determine initial status message
    $status_message = ($initial_backup_status === 'pending') ? 'Backup Pending' : 'Backup Completed';
    // Display initial backup status
    echo "<div class='status " . ($status_message === 'Backup Pending' ? 'pending' : '') . "'>";
    echo "<h2>Backup Status</h2>";
    echo "<p>" . $status_message . "</p>";
    echo "</div>";
    ?>
</div>

        <?php
        // Display backup count
        echo "<div class='status'>";
        echo "<h2>Backup Count</h2>";
        echo "<p>Total Backups: " . $backup_count['count'] . "</p>";
        echo "</div>";

        // Display user count
        echo "<div class='status'>";
        echo "<h2>Number of Users</h2>";
        echo "<p>Total Users: " . $user_count['count'] . "</p>";
        echo "</div>";

        // Display user list
        echo "<div class='user-list'>";
        echo "<h2>User List</h2>";
        echo "<ul>";
        foreach ($user_list['users'] as $user) {
            echo "<li>" . $user . "</li>";
        }
        echo "</ul>";
        echo "</div>";
        ?>
    </div>
    <script>
    // Function to fetch data from the API
    function fetchDataFromApi(url) {
        return fetch(url)
            .then(response => response.json())
            .catch(error => console.error('Error:', error));
    }

    // Function to update the backup status
    function updateBackupStatus() {
        fetchDataFromApi("http://localhost:5000/api/backup/status")
            .then(data => {
                const statusContainer = document.getElementById("statusContainer");
                // Determine status message based on fetched data
                const statusMessage = data.status === 'pending' ? 'Backup Pending' : 'Backup Completed';
                // Update status container HTML
                statusContainer.innerHTML = `
                    <div class="status ${data.status}">
                        <h2>Backup Status</h2>
                        <p>${statusMessage}</p>
                    </div>`;
            });
    }

    // Update dashboard initially and then every 5 seconds
    updateBackupStatus();
    setInterval(updateBackupStatus, 5000); // Update every 5 seconds
</script>


</body>
</html>
