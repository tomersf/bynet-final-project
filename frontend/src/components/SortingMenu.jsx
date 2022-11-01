import React from 'react'
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import { Typography } from '@mui/material';
import _ from 'lodash'


export default function SortingMenu({attendees,setAttendeesList}) {

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
    <div style={{marginTop:'20px', marginBottom: '20px'}}>
    <Typography variant='h4' sx={{color:'white'}}>Sorting Menu</Typography>
    <Stack spacing={2} direction="row">
      <Button variant="outlined" onClick={sortAscending}>Ascending</Button>
      <Button variant="outlined" onClick={sortDescending}>Descending</Button>
      <Button variant="outlined" onClick={random}>Random</Button>
    </Stack>
    </div>)
};
