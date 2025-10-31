package features

import (
	"bytes"
	"cli-top/helpers"
	"cli-top/types"
	"fmt"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

// BuildAIData collects all VTOP data and aggregates it into a single structure for AI features
func BuildAIData(regNo string, cookies types.Cookies) (types.VTOPAIData, error) {
	var data types.VTOPAIData
	var errors []string

	// Initialize with basic info
	data.RegNo = regNo
	data.GeneratedAt = time.Now()

	// Collect Marks
	marks, err := collectAIMarks(regNo, cookies)
	if err != nil {
		errors = append(errors, fmt.Sprintf("marks: %v", err))
	} else {
		data.Marks = marks
	}

	// Collect Attendance
	attendance, err := collectAIAttendance(regNo, cookies)
	if err != nil {
		errors = append(errors, fmt.Sprintf("attendance: %v", err))
	} else {
		data.Attendance = attendance
	}

	// Collect Exams
	exams, err := collectAIExams(regNo, cookies)
	if err != nil {
		errors = append(errors, fmt.Sprintf("exams: %v", err))
	} else {
		data.Exams = exams
	}

	// Collect Timetable
	timetable, err := collectAITimetable(regNo, cookies)
	if err != nil {
		errors = append(errors, fmt.Sprintf("timetable: %v", err))
	} else {
		data.Timetable = timetable
	}

	// Collect CGPA and trend
	cgpa, trend, semester, err := collectAICGPA(regNo, cookies)
	if err != nil {
		errors = append(errors, fmt.Sprintf("cgpa: %v", err))
	} else {
		data.CGPA = cgpa
		data.CGPATrend = trend
		data.Semester = semester
	}

	// Return combined error if any
	if len(errors) > 0 {
		return data, fmt.Errorf("partial data collection errors: %s", strings.Join(errors, "; "))
	}

	return data, nil
}

// collectAIMarks fetches marks for all courses using the latest semester
func collectAIMarks(regNo string, cookies types.Cookies) ([]types.CourseMarksSummary, error) {
	if !helpers.ValidateLogin(cookies) {
		return nil, fmt.Errorf("invalid login")
	}

	url := "https://vtop.vit.ac.in/vtop/examinations/doStudentMarkView"

	// Get latest semester
	semester, err := helpers.SelectSemester(regNo, cookies, 5) // 5 = latest semester
	if err != nil {
		return nil, err
	}

	payload := fmt.Sprintf(
		"------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"authorizedID\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"semesterSubId\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"_csrf\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J--\r\n",
		regNo,
		semester.SemID,
		cookies.CSRF,
	)

	bodyText, err := helpers.FetchReq(regNo, cookies, url, semester.SemID, payload, "POST", "marks")
	if err != nil {
		return nil, err
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyText))
	if err != nil {
		return nil, err
	}

	courseDetails := subjectDetails(doc)
	elements := findElementsByClass(doc, "customTable-level1")

	var marks []types.CourseMarksSummary

	for idx, course := range courseDetails {
		if idx >= len(elements) {
			continue
		}

		selectedElement := elements[idx]
		marksTable, weightageMark, maxMarkSum := ExtractMarks(selectedElement)

		// Convert marksTable ([][]string) to []CourseMarksComponent
		var components []types.CourseMarksComponent
		for _, row := range marksTable {
			if len(row) >= 6 {
				component := types.CourseMarksComponent{
					Title:  row[0],
					Status: row[3],
				}
				// Parse numbers safely
				fmt.Sscanf(row[1], "%f", &component.MaxMarks)
				fmt.Sscanf(row[2], "%f", &component.Weightage)
				fmt.Sscanf(row[4], "%f", &component.ScoredMarks)
				fmt.Sscanf(row[5], "%f", &component.WeightageMark)

				components = append(components, component)
			}
		}

		summary := types.CourseMarksSummary{
			CourseCode:  course.CourseCode,
			CourseTitle: course.CourseTitle,
			CourseType:  course.CourseType,
			Faculty:     course.Faculty,
			Slot:        course.Slot,
			Components:  components,
			TotalScored: weightageMark,
			TotalWeight: float64(maxMarkSum),
		}

		marks = append(marks, summary)
	}

	return marks, nil
}

// collectAIAttendance fetches attendance records using the latest semester
func collectAIAttendance(regNo string, cookies types.Cookies) ([]types.AttendanceRecord, error) {
	if !helpers.ValidateLogin(cookies) {
		return nil, fmt.Errorf("invalid login")
	}

	url := "https://vtop.vit.ac.in/vtop/student/attn_report"

	// Get latest semester
	semester, err := helpers.SelectSemester(regNo, cookies, 5)
	if err != nil {
		return nil, err
	}

	payload := fmt.Sprintf(
		"------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"authorizedID\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"semesterSubId\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"_csrf\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J--\r\n",
		regNo,
		semester.SemID,
		cookies.CSRF,
	)

	bodyText, err := helpers.FetchReq(regNo, cookies, url, semester.SemID, payload, "POST", "attendance")
	if err != nil {
		return nil, err
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyText))
	if err != nil {
		return nil, err
	}

	var attendance []types.AttendanceRecord

	doc.Find("table#attendanceTableId tbody tr").Each(func(i int, row *goquery.Selection) {
		cells := row.Find("td")
		if cells.Length() < 8 {
			return
		}

		courseCode := strings.TrimSpace(cells.Eq(1).Text())
		if courseCode == "" || courseCode == "Course Code" {
			return
		}

		record := types.AttendanceRecord{
			CourseCode: courseCode,
			CourseName: strings.TrimSpace(cells.Eq(2).Text()),
			CourseType: strings.TrimSpace(cells.Eq(3).Text()),
			Faculty:    strings.TrimSpace(cells.Eq(4).Text()),
		}

		// Parse attendance numbers (defensive parsing)
		fmt.Sscanf(strings.TrimSpace(cells.Eq(5).Text()), "%d", &record.Attended)
		fmt.Sscanf(strings.TrimSpace(cells.Eq(6).Text()), "%d", &record.Total)
		fmt.Sscanf(strings.TrimSpace(cells.Eq(7).Text()), "%f", &record.Percentage)

		attendance = append(attendance, record)
	})

	return attendance, nil
}

// collectAIExams fetches exam schedule for all semesters
func collectAIExams(regNo string, cookies types.Cookies) ([]types.ExamEvent, error) {
	if !helpers.ValidateLogin(cookies) {
		return nil, fmt.Errorf("invalid login")
	}

	url := "https://vtop.vit.ac.in/vtop/examinations/doSearchExamScheduleForStudent"

	allSems, err := helpers.GetSemDetails(cookies, regNo)
	if err != nil {
		return nil, err
	}

	if len(allSems) == 0 {
		return nil, fmt.Errorf("no semesters found")
	}

	// Try semesters from latest to oldest
	for i := len(allSems) - 1; i >= 0; i-- {
		semID := allSems[i].SemID
		bodyText, err := helpers.FetchReq(regNo, cookies, url, semID, "UTC", "POST", "")
		if err != nil {
			continue
		}

		doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyText))
		if err != nil {
			continue
		}

		exams, err := parseExamSchedule(doc)
		if err == nil && len(exams) > 0 {
			return exams, nil
		}
	}

	return []types.ExamEvent{}, nil
}

// collectAITimetable fetches weekly timetable using latest semester
func collectAITimetable(regNo string, cookies types.Cookies) ([]types.TimetableEntry, error) {
	if !helpers.ValidateLogin(cookies) {
		return nil, fmt.Errorf("invalid login")
	}

	url := "https://vtop.vit.ac.in/vtop/examinations/doSearchCandidateTimetable"

	semester, err := helpers.SelectSemester(regNo, cookies, 5)
	if err != nil {
		return nil, err
	}

	payload := fmt.Sprintf(
		"------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"authorizedID\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"semesterSubId\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J\r\nContent-Disposition: form-data; name=\"_csrf\"\r\n\r\n%s\r\n------WebKitFormBoundary9yjNZXu7BBjgQK7J--\r\n",
		regNo,
		semester.SemID,
		cookies.CSRF,
	)

	bodyText, err := helpers.FetchReq(regNo, cookies, url, semester.SemID, payload, "POST", "timetable")
	if err != nil {
		return nil, err
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyText))
	if err != nil {
		return nil, err
	}

	var timetable []types.TimetableEntry
	days := []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

	// Parse timetable table
	doc.Find("table tbody tr").Each(func(rowIdx int, row *goquery.Selection) {
		if rowIdx >= len(days) {
			return
		}
		day := days[rowIdx]

		row.Find("td").Each(func(colIdx int, cell *goquery.Selection) {
			if colIdx == 0 { // Skip day column
				return
			}

			content := strings.TrimSpace(cell.Text())
			if content == "" || content == "-" {
				return
			}

			entry := types.TimetableEntry{
				Day: day,
			}

			// Try to parse content (simplified)
			lines := strings.Split(content, "\n")
			if len(lines) > 0 {
				entry.Course = strings.TrimSpace(lines[0])
			}

			timetable = append(timetable, entry)
		})
	})

	return timetable, nil
}

// collectAICGPA fetches CGPA and historical trend
func collectAICGPA(regNo string, cookies types.Cookies) (float64, []types.CGPASnapshot, string, error) {
	if !helpers.ValidateLogin(cookies) {
		return 0, nil, "", fmt.Errorf("invalid login")
	}

	url := "https://vtop.vit.ac.in/vtop/examinations/examGradeView/StudentGradeHistory"

	bodyText, err := helpers.FetchReq(regNo, cookies, url, "", "", "POST", "")
	if err != nil {
		return 0, nil, "", err
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(bodyText))
	if err != nil {
		return 0, nil, "", err
	}

	var trend []types.CGPASnapshot
	var currentCGPA float64
	var semester string

	// Parse CGPA table
	doc.Find("table.customTable tbody tr").Each(func(i int, row *goquery.Selection) {
		cells := row.Find("td")
		if cells.Length() < 3 {
			return
		}

		sem := strings.TrimSpace(cells.Eq(0).Text())
		if sem == "" || sem == "Semester" {
			return
		}

		snapshot := types.CGPASnapshot{
			Semester: sem,
		}

		fmt.Sscanf(strings.TrimSpace(cells.Eq(2).Text()), "%f", &snapshot.CGPA)

		// Keep track of latest semester and CGPA
		if snapshot.CGPA > currentCGPA {
			currentCGPA = snapshot.CGPA
			semester = sem
		}

		trend = append(trend, snapshot)
	})

	return currentCGPA, trend, semester, nil
}
