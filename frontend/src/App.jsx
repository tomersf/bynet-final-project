import axios from "axios";
import Lottie from "react-lottie"
import { useState, useEffect } from "react";

import "./App.css";
import AttendeesList from "./components/AttendeesList";
import Menu from './components/Menu';
import TotalAttendance from './components/TotalAttendance'
import loadingAnimation from './animations/loadingAnimation.json'

function App() {
  const [attendeesList,setAttendeesList] = useState([])
  const [totalMeetingsDuration,setTotalMeetingsDuration] = useState(0)
  const [loading,setLoading] = useState(true)

  const fetchAttendees = async () => {
      const attendeesResponse = await axios.get('/api/attendees');
      return JSON.parse(attendeesResponse.data.result)
  }

  const fetchMeetingsDuration = async () => {
    const meetingsDurationResponse =  await axios.get('/api/attendance');
    return JSON.parse(meetingsDurationResponse.data.result)
  }

  const delay = new Promise((resolve, reject) => {
    setTimeout(resolve, 2500);
  });

  const reloadData = async () => {
    setLoading(true)
    const reloadResponse = await axios.get('/api/reload-data');
    if (reloadResponse.data.result === true) {
      await fetchMeetingsDuration()
      await fetchAttendees()
    }
    setLoading(false)
  }


  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      const [meetingsDuration, attendees] = await Promise.all([fetchMeetingsDuration(),fetchAttendees(),delay])
      setLoading(false)
      setAttendeesList(attendees)
      setTotalMeetingsDuration(parseFloat(meetingsDuration.total_duration).toFixed(2));
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
      <Menu attendees={attendeesList} setAttendeesList={setAttendeesList} reloadData={reloadData}/>
      <AttendeesList attendees={attendeesList}/>
    </div>
  );
}

export default App;
