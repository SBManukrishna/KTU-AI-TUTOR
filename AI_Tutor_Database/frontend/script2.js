document.addEventListener("DOMContentLoaded", function () {
    const courseSelect = document.getElementById("course-select");
    const contentDiv = document.querySelector(".syllabus-div");

    // Fetch courses and populate dropdown
    function fetchCourses() {
        fetch("http://127.0.0.1:5000/api/courses")
            .then(response => response.json())
            .then(courses => {
                courseSelect.innerHTML = '<option value="">Select a Course</option>';
                courses.forEach(course => {
                    const option = document.createElement("option");
                    option.value = course.id;
                    option.textContent = `${course.course_code} - ${course.course_title}`;
                    courseSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Error fetching courses:", error));
    }

    // Fetch syllabus when a course is selected
    function fetchSyllabus(courseId) {
        fetch(`http://127.0.0.1:5000/api/syllabus?course_id=${courseId}`)
            .then(response => response.json())
            .then(data => {
                contentDiv.innerHTML = ""; // Clear previous content

                if (!data || data.length === 0) {
                    contentDiv.innerHTML = "<p>No syllabus available for this course.</p>";
                    return;
                }

                let syllabusHTML = `<h2>Course Syllabus</h2>`;
                
                data.forEach(module => {
                    syllabusHTML += `
                        <div class="module">
                            <h3>Module ${module.module_number}: ${module.module_title} (${module.duration})</h3>
                            <ul>`;
                    
                    module.topics.forEach(topic => {
                        syllabusHTML += `
                            <li>
                                <a href="#" class="topic-link" data-title="${topic.title}" data-time="${topic.time}" data-content="${topic.content}">
                                    ${topic.number}. ${topic.title}
                                </a>
                            </li>`;
                    });

                    syllabusHTML += "</ul></div>";
                });

                contentDiv.innerHTML = syllabusHTML;

                // Add click event to topic links
                document.querySelectorAll(".topic-link").forEach(link => {
                    link.addEventListener("click", function (event) {
                        event.preventDefault();
                        displayTopicContent(this);
                    });
                });
            })
            .catch(error => console.error("Error fetching syllabus:", error));
    }

    // Display topic content when clicked
    function displayTopicContent(topicElement) {
        const title = topicElement.getAttribute("data-title");
        const time = topicElement.getAttribute("data-time");
        const content = topicElement.getAttribute("data-content");
    
        contentDiv.innerHTML = `
            <h2>${title}</h2>
            <p><strong>Estimated Time:</strong> ${time} min</p>
            <div class="topic-content">${marked.parse(content)}</div>
            <button id="backButton">Back to Syllabus</button>
        `;
    
        // Add back button functionality
        document.getElementById("backButton").addEventListener("click", function () {
            const selectedCourseId = courseSelect.value;
            if (selectedCourseId) fetchSyllabus(selectedCourseId);
        });
    }
    

    // Load courses on page load
    fetchCourses();

    // Fetch syllabus when a course is selected
    courseSelect.addEventListener("change", function () {
        const selectedCourseId = this.value;
        if (selectedCourseId) {
            fetchSyllabus(selectedCourseId);
        } else {
            contentDiv.innerHTML = "<p>Please select a course.</p>";
        }
    });
});
