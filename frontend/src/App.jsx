import axios from "axios";
import Lottie from "react-lottie"
import { useState, useEffect } from "react";

import "./App.css";
import AttendeesList from "./components/AttendeesList";
import SortingMenu from './components/SortingMenu';
import TotalAttendance from './components/TotalAttendance'
import loadingAnimation from './animations/loadingAnimation.json'

function App() {
  const [attendeesList,setAttendeesList] = useState([])
  const [totalMeetingsDuration,setTotalMeetingsDuration] = useState(0)
  const [loading,setLoading] = useState(true)

  const fetchAttendees = async () => {
      const attendees = await axios.get('/api/attendees');
      return attendees
  }

  const fetchMeetingsDuration = () => {
    const meetingsDuration =  axios.get('/api/attendance');
    return meetingsDuration
  }

  const delay = new Promise((resolve, reject) => {
    setTimeout(resolve, 2500);
  });


  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const [meetingsDuration, attendees] = await Promise.all([fetchMeetingsDuration(),fetchAttendees(),delay])
      setLoading(false)
      setAttendeesList(attendees.data)
      setTotalMeetingsDuration(parseFloat(meetingsDuration.data.total_duration).toFixed(2));
    }
    fetchData()
  },[]);

  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: loadingAnimation,
    rendererSettings: {
      preserveAspectRatio: "xMidYMid slice",
    },
  };

  if(loading) {
    return (
      <div className="App">
          <Lottie options={defaultOptions} height={400} width={400} />
      </div>
    )
  }

  return (
    <div className="App">
      <TotalAttendance duration={totalMeetingsDuration} />
      <SortingMenu attendees={attendeesList} setAttendeesList={setAttendeesList}/>
      <AttendeesList attendees={attendeesList}/>
    </div>
  );
}

export default App;
