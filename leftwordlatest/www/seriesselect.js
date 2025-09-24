// $(document).ready(function () {
//     $('#done-btn').on('click', function (e) {
//         e.preventDefault(); // Prevent default action

//         // Collect checked series names
//         let selectedSeriesNames = [];
//         $('#series-checkbox-list input[type="checkbox"]:checked').each(function () {
//             const seriesName = $(this).closest('label').text().trim(); 
//             selectedSeriesNames.push(seriesName); // Add the name to the array
//         });

//         // Check if any series is selected
//         if (selectedSeriesNames.length > 0) {
//             console.log("Selected Series Names: ", selectedSeriesNames); // Log selected series names to the console
//             // alert("Selected Series: " + selectedSeriesNames.join(", ")); // Alert the selected series names
//         } else {
//             alert("No series selected!"); // Alert if no series is selected
//         }
//     });
// });