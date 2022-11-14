import React from 'react'
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import { Typography } from '@mui/material';
import _ from 'lodash'


export default function Menu({attendees,setAttendeesList, reloadData}) {

  const sortAscAttendees = (attendeeA,attendeeB) => {
    const res = parseInt(attendeeA.attendance_duration
      ) > parseInt(attendeeB.attendance_duration
      ) ? 1 : -1
    return res;
  }
  const sortAscending = () => {
   attendees.sort(sortAscAttendees)
   const newArray = attendees.map(a => ({...a}));
    setAttendeesList(newArray)
  }
  const sortDescending = () => {
    attendees.sort((attendeeA,attendeeB) => {
      const result = sortAscAttendees(attendeeA,attendeeB)
      if (result === 1) return -1
      else return 1
    })
      const newArray = attendees.map(a => ({...a}));
      setAttendeesList(newArray)
  }
  const random = () => {
    const shuffledAttendees = _.shuffle(attendees)
    setAttendeesList(shuffledAttendees)
  }

  return (
    <div style={{marginTop:'20px', marginBottom: '20px', width: '100%'}}>
    <Typography variant='h4' sx={{color:'white',marginBottom:'10px'}}>Sorting Menu</Typography>
    <Stack spacing={2} direction="row" style={{ textAlign: 'center', position:'relative',justifyContent: 'center'}}>
      <Button variant="outlined" onClick={sortAscending} style={{width: 125}}>Ascending</Button>
      <Button variant="outlined" onClick={sortDescending} style={{width: 125}}>Descending</Button>
      <Button variant="outlined" onClick={random} style={{width: 125}}>Random</Button>
      <Button variant="outlined" onClick={reloadData} style={{width: 125,position: 'absolute',right:6}}>FETCH DATA</Button>
    </Stack>
    </div>)
};
