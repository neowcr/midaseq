#*# ____//―――――― Settings ――――――\\____#*#
setting = {
    "overrideAllPrograms" : {
        "value": -1,
        "description": "Overrides all program changes to be specified instrument value."
    },
    "ignoreDrumChannel" : {
        "value": False,
        "description": "Ignores midi channel 10 from the input."
    },
    "enable_debugPrinting" : {
        "value": False,
        "description": "Displays additional information. Only useful for debugging, as it slows down the program."
    },
    "enable_runningStatusWriting" : {
        "value": True,
        "description": "Enable Running Status optimization."
    },
    "enable_optimizeRedundantChannelParams" : {
        "value": False,
        "description": "This makes so, for example, the first volume change of the MIDI is put before the main sequence itself, making the file slightly more organized."
    },
    "remove_duplicateEvents" : {
        "value": True,
        "description": "Removes unnecessary events that are exactly the same as others. (Specially useful for FL Studio MIDIs)"
    }
}




 

 

                                                  
                                                  

print(r"  __  __ _____ _____           _____ ______ ____    ")
print(r" |  \/  |_   _|  __ \   /\    / ____|  ____/ __ \   ")
print(r" | \  / | | | | |  | | /  \  | (___ | |__ | |  | |  ")
print(r" | |\/| | | | | |  | |/ /\ \  \___ \|  __|| |  | |  ")
print(r" | |  | |_| |_| |__| / ____ \ ____) | |___| |__| |  ")
print(r" |_|  |_|_____|_____/_/    \_\_____/|______\___\_\  ")
print("")
print("Version 0.8")
print("Made by: Neoware (nwcr)")
print("exe version made with PyInstaller")





import math
import os
import sys

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    print("")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!! E R R O R |||||||||||||||||| E R R O R !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
    traceback.print_exception(exc_type, exc_value, tb)
    input("\nPress key to exit.")
    sys.exit()


sys.excepthook = show_exception_and_exit



allowConfigAtRuntime = True; #If True, asks for settings at runtime

#Detect if running from a python script and disable config stuff
our_path = sys.argv[0];
our_file_extension = os.path.splitext( os.path.basename(our_path)) [1];
if (our_file_extension == ".py"):
    allowConfigAtRuntime = False;
    pass;
else:
    #In case I mess up and leave these in the incorrect default values when testing
    setting["enable_debugPrinting"]["value"] = False;
    allowConfigAtRuntime = True





if (allowConfigAtRuntime):
    isGonnaChangeSettings = input("Wish to change any settings? [y/n]\n")
    isGonnaChangeSettings = isGonnaChangeSettings.lower();
    isGonnaChangeSettings += " ";


    if (isGonnaChangeSettings[0] == "y" ):
        

        for cfg_id in setting:
            _default_value = setting[cfg_id]['value'];

            print("");
            print( cfg_id);
            print( "\"" + ( setting[cfg_id]['description'] ) + "\"");
            print( "Default Value: ", _default_value);
            print("(Leave nothing to set as default)");
            print("");

            change_value = input( "Type value and press Enter.\n" );
            if (change_value != "" and change_value != " "):


                change_value = change_value.lower();
                

                if( isinstance(_default_value, bool) ):

                    if (change_value == "true" or change_value == "tru" or change_value == "1"):
                        change_value = True;
                    elif (change_value == "false" or change_value == "0"):
                        change_value = False;
                    else:
                        change_value = _default_value;



                elif( isinstance(_default_value, int) ):
                    change_value = int( change_value );


                setting[cfg_id]["value"] = change_value;




setting["overrideAllPrograms"]["value"] = int( setting["overrideAllPrograms"]["value"] );
print( setting );





def dprint( *args ):
    if ( setting["enable_debugPrinting"]["value"]):
        print( *args );

def print_topic( *args ):
    print( "  ■ ▲        /───────────── " , "log-topic: ", *args )
    print( "  𐄂 ● ______/")


def bytes2hex( _bytes ):
    return _bytes.hex(sep=' ');

midi_event_table = {
    0x8 : {
        "name": "Note Off",
        "byte_length": 3,
        "type": "Voice"
    },
    0x9: {
        "name": "Note On",
        "byte_length": 3,
        "type": "Voice"
    },
    0xB: {
        "name": "Control Change (CC)",
        "byte_length": 3,
        "type": "Voice"
    },
    0xC: {
        "name": "Program Change",
        "byte_length": 2,
        "type": "Voice"
    },
    0xE: {
        "name": "Pitch Bend",
        "byte_length": 3,
        "type": "Voice"
    }
}



#How many ticks are in a quarter note, default is 48
tick_resolution : int = 48;
song_bpm : int = None;
song_timesig = [];
track_amount : int = 16; #maximum 16 for now 
hasLoopEvent = False;





starting_channel_program = [None] * track_amount;
starting_channel_vol = [None] * track_amount;
starting_channel_pan = [None] * track_amount;




#Explanation (outdated)
# 1 - Read MIDI file and for each event we read, we put that in the event_list
#          format: track , absolute time, event in hex (minus delta)
# 2 - We loop through each track in event_list, going through time
#     ignoring the ones that happen after the current time passed.
#     Then we make a new list, but with just one track and delta times
#     followed by the event data
#          format: new delta time, event in hex (minus delta)
# 3 - We read through this merged list and then write the SEQ as we read it

#Abstracted events
event_list = [];
merged_event_list = [];


latest_time = 0;


def decode_vlq( byte_sequence, read_pos ):
    total_value = 0;

    while True:
        current_byte = byte_sequence[read_pos];
        current_byte = current_byte.to_bytes(1,"big");
        
        total_value |= current_byte[0] & (b'\x7F')[0] ;

        
        has_variable_len = current_byte[0] & (b'\x80')[0];
        
        if (has_variable_len != 0):
            #dprint( current_byte );
            total_value = total_value << 7;
            
            read_pos += 1;
        else:
            break;

    #dprint("total - ", total_value)
    #Return the total value and the reading position, relative to the initial position
    return_list = [read_pos, total_value];
    return return_list;



def int2byte( int_val : int ):
    return int_val.to_bytes(1,"big");




#Step 1

input_bytes = [];
input_trackData = [];
input_formatType : bytes = b'\x01';
input_trackCount : bytes = b'\x01';
input_tick : bytes = b'\x60'; #Default I set is 96 but doesnt really matter tbh
input_tempo : bytes = b'\x06\x1A\x80'; #150 BPM by default, or 400000 ticks per quarter note


def read_input_file( file_path ):
    global input_bytes;
    global input_trackData;
    global input_formatType;
    global input_trackCount;
    global input_tick;


    with open(file_path, 'rb') as inputFile:
        input_bytes = inputFile.read();




        print_topic("init reading header");
        dprint( input_bytes );


        if (input_bytes[0:4] == b'MThd'):
            dprint( "correct signature" );
        else:
            dprint("wrong signature :(" );
            sys.exit();

        
        chunk_length : int = int.from_bytes(input_bytes[4:8]);
        read_pos = 8; #We'll start reading from byte 8, because its after the chunk length

        print("\nreading header chunk data")
        current_chunk = input_bytes[ read_pos:(read_pos+chunk_length) ];

        input_formatType = current_chunk[0:2];
        input_trackCount = current_chunk[2:4];
        input_tick = current_chunk[4:6];
        
        print( "format type: " , int.from_bytes(input_formatType)  );
        print( "track count: " , int.from_bytes(input_trackCount)  );
        print( "tick resolution: " , int.from_bytes(input_tick)  );

        read_pos += chunk_length;
        
        print("done reading header!\n");

        
        for input_track in range( int.from_bytes(input_trackCount) ):
            print("log-topic: init reading chunk no. " , 1 + input_track);

            dprint("signature " , input_bytes[ read_pos:(read_pos+4) ] )
            chunk_length = input_bytes[ (read_pos+4):(read_pos+8) ]
            chunk_length = int.from_bytes(chunk_length) ;
            
            dprint("size " , chunk_length )
            read_pos += 8;

            
            input_trackData.append(input_bytes[read_pos : (read_pos+chunk_length)]);
            dprint("track data:\n");
            dprint( input_trackData[input_track] );
            dprint("\n");
            read_pos += chunk_length;

        

        print("\ninput file done loading");




input_file = "";
default_file = "input.mid"
output_path = "output.seq";


if ( len(sys.argv) > 1 ):
    input_file = sys.argv[1]; #Get the file path from dragged files
    output_path = os.path.splitext(os.path.basename(input_file))[0] + ".seq";
else:
    input_file = default_file;
    


if os.path.exists(input_file):
    read_input_file( input_file )
else:
    print("ERROR: No input file found.")
    print("Try dragging a file onto the program, or putting a file named input.mid in the same directory");
    input("Press any key to exit...")
    sys.exit();




















def encode_vlq( value : int ):
    value_bin = bin( value );
    value_bin = value_bin[2::] #Cut the '0b' in the start of the string
    value_bin_len = len( value_bin );
    #Turn value into binary
    #dprint(  value_bin  );

    #Divide into groups of 7
    byte_chunks = value_bin_len / 7;
    byte_chunks = math.ceil( byte_chunks );
    #dprint("chunks ", byte_chunks);


    bin_chunks = [];

    vlq_bin = [];

    for c in range(byte_chunks):

        
        slice_end = value_bin_len - (7*c) ;
        slice_start = max( slice_end - 7,  0);
        
        
        bin_chunks.append( value_bin[ slice_start : slice_end ] );

        #Pad the missing bits to form a 7-bit chunk
        if len(bin_chunks[c]) < 7:
            padding_needed = 7 - len(bin_chunks[c]);

            padding_str = "0" * padding_needed;
            
            bin_chunks[c] = padding_str + bin_chunks[c];
            #dprint("padding need : " , padding_needed)
            pass;

    bin_chunks.reverse()
    #dprint(bin_chunks);


    for c in range(byte_chunks):
        MSB = 1;
        #If last chunk, MSB is 0
        if (c == (byte_chunks - 1)):
            MSB = 0;
        
        vlq_bin.append( str(MSB) + bin_chunks[c] );
        pass;

    #dprint(vlq_bin);
    
    vlq_bytes = "".join(vlq_bin);
    vlq_bytes = int(vlq_bytes,2);
    
    vlq_bytes = vlq_bytes.to_bytes(byte_chunks , 'big');
    
    #dprint(vlq_bytes)
    return vlq_bytes;
    pass;



def write_delta ( delta_time ):
    #Delta time
    if (delta_time > int.from_bytes(b'\x7F' ) ):
        #If MSB is 1, its a variable length quantity
        file.write( encode_vlq(delta_time) );
    else:
        file.write ( delta_time.to_bytes(1, byteorder='big') ); 

def write_event( delta_time, _id : str , _track_number ):
    write_delta(delta_time);
     

    _hex_track_number : str = format(_track_number,"x");
    file.write ( bytes.fromhex( _id + _hex_track_number ) ); #xCn  (n = track number)



def write_control_change( delta_time , _track_number, control_id , set_value ):
    write_event(delta_time, "B", _track_number);

    file.write ( control_id.to_bytes(1, byteorder='big') );
    file.write ( set_value.to_bytes(1, byteorder='big') );

def write_program_change( delta_time , _track_number, program_id ):
    write_event(delta_time, "C", _track_number);

    file.write ( program_id.to_bytes(1, byteorder='big') );

def write_loop_start():
    write_control_change(0, 0, 99, 20);


    
def write_loop_end(delta_time):
    write_control_change(delta_time, 0, 99, 30);




def write_note( delta_time , _track_number, note_pitch, _velocity ):
    write_event(delta_time, "9", _track_number);

    file.write ( note_pitch.to_bytes(1, byteorder='big') );
    file.write ( _velocity.to_bytes(1, byteorder='big') );



def pow_to_denominator( _pow ):
    return 1 << _pow;

def denominator_to_pow( real_denominator ):
    _m = 0;
    _r = 0;
    while _r < real_denominator:
        _r = (1 << _m)
        _m += 1

    return _m - 1;


def remove_duplicates( og_list ):
    tuplified = og_list;

    #Turn list into tuples, and its insides to tuples as well
    for _t in range( len(tuplified) ):
        tuplified[_t] = tuple(tuplified[_t])

    tuplified = tuple(tuplified);

    return list( dict.fromkeys(tuplified) );


def convert_event( _track_id , initial_read_pos : int , absolute_time : int , running_status : bytes ):
    #Reads and writes to event_list with absolute time
    _running = running_status;

    track_data = input_trackData[_track_id];
    _pos = initial_read_pos;

    ##Find out the event
    current_byte = track_data[_pos];
    event_byte = int2byte(current_byte);

    #Give up if we're at the end of track
    if (  (_pos+1) >= len(track_data) ):
        return [_pos , _running];

    skip_listing = False;

    #Check if its a meta event first "FF" byte
    if (event_byte == b'\xFF'):
        dprint("-meta event")
        metaEvent_type = int2byte( track_data[_pos + 1] );
        
        
        test_var_length = decode_vlq( track_data , _pos + 2 );
        

        metaEvent_dataStart = 1 + test_var_length[0];
        metaEvent_dataEnd = metaEvent_dataStart + test_var_length[1];
        metaEvent_data = track_data[ (metaEvent_dataStart) : (metaEvent_dataEnd) ];
        
        

        metaEvent_typeDebugText = "text-related, dont care";
        
        match (metaEvent_type) :
            case b'\x51':
                #Tempo - FF 51 03 tt tt tt
                metaEvent_typeDebugText = "Tempo"
                tempo_val = track_data[ (_pos + 3) : (_pos + 6) ];

                global song_bpm;

                if (song_bpm == None):
                    #First tempo event, so we're gonna set this variable here
                    dprint("FIRST TEMPOOO")
                    seconds_per_beat = int.from_bytes(tempo_val) / 1000000;
                    spb_to_bpm = 60 / seconds_per_beat;
                    song_bpm = spb_to_bpm;
                    skip_listing = True;

                #event_list[_track_id].append( track_data[ (_pos) : (_pos + 6) ] );

                
                pass;
            case b'\x58':
                #Time Signature - FF 58 04 nn dd cc bb
                metaEvent_typeDebugText = "Time Signature"

                global song_timesig;

                if (song_timesig == [] ):
                    dprint("FIRST TIME SIGGG")
                    timesig_numerator =  track_data[_pos + 3]
                    timesig_denominator = pow_to_denominator(   track_data[_pos + 4]    );
                    song_timesig = [ timesig_numerator , timesig_denominator ];
                    dprint(song_timesig);
                    skip_listing = True;

                pass;
            case b'\x2F':
                #Track End
                metaEvent_typeDebugText = "Track End"
                
                #tracks_finished[_track_number] = True;

        
        dprint( "meta event type: " , metaEvent_typeDebugText );
        dprint( "event data read pos: ", test_var_length[0]  );
        dprint("event data length: ", test_var_length[1]  );
        dprint( "event data: ", metaEvent_data );
        dprint( "entire event: ", track_data[ (_pos) : (metaEvent_dataEnd) ] );

        if (not skip_listing):
            event_list[  _track_id ].append( [absolute_time , track_data[ (_pos) : (metaEvent_dataEnd) ]  ] );

        #Go to next event
        _pos = metaEvent_dataEnd;

    else:
        dprint("-voice event");

        _event_data_pos = _pos;

        is_runningStatus = 0;

        #See if should apply running status or not
        if ( event_byte < b'\x80' ):
            event_byte = _running;
            is_runningStatus = 1;
            dprint( "running status should be applied" );
            _event_data_pos = _pos - 1; #This byte is already the data, not the event byte, so go back
        else:
            #Check first nibble to see type, second nibble for the channel
            _running = event_byte;

        event_typeId = (event_byte[0] >> 4);
        event_channel = event_byte[0] & b'\x0F'[0];   
        event_typeDebugText = ""
        
         
        event_length = 0;

        
        #Identify event
        if (event_typeId in midi_event_table):
            event_length = midi_event_table[  event_typeId ]["byte_length"];
            event_data = track_data[ (_pos) : ( _pos + (event_length - is_runningStatus) ) ];

            event_typeDebugText = midi_event_table[  event_typeId ]["name"];
            

            #Add implied event if there's running status
            if( is_runningStatus == 1 ):
                
                dprint( "event data: ", event_data.hex(sep = " ") )
                new_prefix = format(event_typeId,"x") + format(event_channel,"x");
                event_data = bytes.fromhex(new_prefix) + event_data;




            #This detects the first occurences of certain events
            #and either puts them after the seq header before the loop start
            #or leaves them out entirely if they're just setting up default values
            #(the generic driver seems to already set up the defaults)

            if ( setting["enable_optimizeRedundantChannelParams"]["value"] ):
                global starting_channel_vol
                global starting_channel_pan
                global starting_channel_program

                if ( midi_event_table[event_typeId]["name"] == "Control Change (CC)" ):
                    control_id = event_data[1];
                    control_value = event_data[2];

                    #starting_channel_program = [] * track_amount;
                    #starting_channel_vol = [] * track_amount;
                    #starting_channel_pan = [] * track_amount;

                    if (control_id == 7):
                        #Volume
                        if ( starting_channel_vol[ event_channel ] == None ):
                            dprint("First volume setting")
                            skip_listing = True;

                            if (control_value != 100):
                                #Disregard if we're just setting to default anyway
                                starting_channel_vol[ event_channel ] = control_value;
                    elif (control_id == 10):
                        #Panning
                        if ( starting_channel_vol[ event_channel ] == None ):
                            dprint("First volume setting")
                            skip_listing = True;

                            if (control_value != 64):
                                #Disregard if we're just setting to default anyway
                                starting_channel_pan[ event_channel ] = control_value;


                elif ( midi_event_table[event_typeId]["name"] == "Program Change" ):
                    #Program change
                    program_id = event_data[1];

                    if ( starting_channel_program[ event_channel ] == None  ):
                        skip_listing = True;

                        if ( program_id != event_channel ):
                            #Disregard if we're just setting to default anyway
                            starting_channel_program[ event_channel ] = program_id;




            #Is it a loop event?
            if ( event_data == b'\xb0\x63\x14' ):
                global hasLoopEvent;
                if ( not hasLoopEvent ):
                    print("First Loop point found")
                    hasLoopEvent = True;
                else:
                    skip_listing = True;

            if ( event_channel == 10 and setting["ignoreDrumChannel"]["value"]  ):
                skip_listing = True;

            #Add to list
            if (not skip_listing):
                event_list[  _track_id ].append( [absolute_time , event_data] );





            

            dprint("");
            dprint( "event type: " , event_typeDebugText );
            dprint( "event channel: " , event_channel );
            dprint( "event data: ", event_data.hex(sep = " ") )

        else:
            dprint("NO EVENT FOUND!!!!! //// I REPEAT, NO EVENT FOUND!!!!!! <:O")

        

        
        _pos += event_length - is_runningStatus;

        

        dprint("__");
        dprint(" initial_read_pos " , initial_read_pos);
        dprint(" _pos " , _pos);

        

    return [_pos , _running];
    pass;



def read_and_list():
    print("")
    print_topic("step 2 - read and list");

    global input_trackData;

    input_trackData = tuple(input_trackData);

    track_number = int.from_bytes(input_trackCount);
    absolute_time = [0] * track_number;

    dprint( len(input_trackData) );
    for _t in range( track_number ):
        event_list.append( [] )

        reading_track = input_trackData[_t];

        running_status : bytes = b'\x00';
        read_pos : int = 0;

        track_data_length = len(reading_track);

        #Main event reading
        while read_pos < (track_data_length - 1):
            dprint("[+] event")
            test_var_length = decode_vlq( reading_track , read_pos );
            read_pos = 1 + test_var_length[0];
            delta = test_var_length[1];
            dprint("delta: ", delta);

            absolute_time[_t] = absolute_time[_t] + delta;
            dprint("absolute time:", absolute_time[_t] )

            global latest_time;

            if ( absolute_time[_t]  >  latest_time  ) :
                latest_time = absolute_time[_t];
            
            _update = convert_event( _t , read_pos , absolute_time[_t], running_status );
            read_pos = _update[0];
            running_status = _update[1];

            pass;

        print("done converting and listing track no. " , _t);

        



def merge_list():
    ##WHEN YOU WRITE THE LIST, MAKE A VARIABLE TO SAVE THE BIGGEST ABSOLUTE TIME THERE IS
    ##IN THE FUNCTION ABOVE
    

    track_number = int.from_bytes(input_trackCount);
    current_time = 0;

    longest_track = max( event_list , key=len );
    longest_track_id = event_list.index( longest_track ) ;
    last_time = 0;

    print("")
    print_topic("step 3 - merge event list")

    #dprint( event_list[2] );
    dprint("")

    passed_time = 0;
    next_time = passed_time;

    last_time_of_track = [ 0 ] * track_number;
    last_index_of_track = [ 0 ] * track_number;
    track_finished_reading = [ False ] * track_number;
    #track_catchup = [0] * track

    global latest_time;
    global merged_event_list;

    while ( passed_time < latest_time ):

            for _t in range( track_number ):
                

                dprint("// Track ", _t)

                current_track = event_list[ _t];

                if (current_track == [] or track_finished_reading[_t] == True):
                    continue; #skip to next iteration if this track is empty
                    #or if finished reading track

                i = last_index_of_track[_t];
                

                #while( current_track[i][0] <= passed_time ):
                current_event = current_track[i];


                if current_event[0] > passed_time:
                    dprint("This event happens later so we're skipping it")
                    last_time_of_track[_t] = current_track[i + 1][0];
                    continue;

                dprint( "reading position:  " , i );
                dprint( current_event )

                merged_event_list.append( current_event );


                if (i >= len(current_track) - 1):
                    dprint("that was the last event of track!")
                    track_finished_reading[_t] = True;
                    
                else:
                    next_event = current_track[i + 1]

                    if (next_event[0] > current_event[0]):
                        last_time_of_track[_t] = next_event[0];


                    i += 1;
                    last_index_of_track[_t] = i;
                    
                 
            dprint("")
            dprint("")

            dprint("FINISHED GOING THROUGH ALL TRACKS, HERE ARE THE RESULTS")
            dprint( "last_time_of_track", last_time_of_track );
            dprint( "last_index_of_track", last_index_of_track )
            dprint( "track_finished_reading", track_finished_reading );
            track_lengths = [];

            for i in event_list:
                track_lengths.append( len(i) );
            dprint(" track_lengths " , track_lengths )
            dprint(" ")


            #Check if there's still a track left to catch up
            remaining_times = [];
            for _t in range(track_number):
                if ( not track_finished_reading[_t] ):
                    remaining_times.append( last_time_of_track[_t] )

            if (  remaining_times != [] and min(remaining_times) <= passed_time  ):
                next_time = passed_time;
                dprint("wait for catching up...")
            else:
            
                if max( last_time_of_track ) > passed_time:
                    next_time = min(i for i in last_time_of_track if i > passed_time)

                
            dprint("")
            dprint( "next time:" , next_time );
            dprint("")
            dprint("")
            passed_time = next_time;

    if ( setting["remove_duplicateEvents"]["value"] ):
        dprint("cleaning up duplicates from merged list");
        merged_event_list = remove_duplicates( merged_event_list );


    #Sort from lowest absolute time to highest, so there is no risk of negative delta
    merged_event_list.sort(key=lambda item: item[0] );

    print("merged list complete!")

    
    for i in merged_event_list:
        dprint( i[0], ", " , bytes2hex(i[1]) );


    dprint("...");


def main_sequence():
    

    running_status = 0;

    #We're gonna use our own delta times in case we decide to not write certain events, thus possibly affecting delta times
    prev_absolute = 0;

    for e in merged_event_list:
        event_absolute = e[0];

        event_delta = event_absolute - prev_absolute;
        event_data = e[1];
        first_byte = event_data[0];

        out_event = b'';

        dprint(" absolute time " , event_absolute )
        dprint( "delta: " , event_delta )

        if ( first_byte == 0xFF ):
            #Meta Event

            

            dprint("WRITING META EVENT")

            #Currently only supporting tempo
            if ( event_data[ 1 ] == 0x51 ):
                dprint("and its tempo!!")

                #dprint( event_data.hex(,sep) );
                #dprint( event_data[2:].hex() );

                out_event += b'\xFF'
                out_event += b'\x51'
                out_event += event_data[3:];

                write_delta( event_delta )
                file.write(out_event);
            elif ( event_data[ 1 ] == 0x58 ) and 0 == 1:
                #Apparently seq doesnt support time signature meta events?? At least is what VGMTrans tells me
                dprint("and its time sig!!")
                #dprint( event_data.hex(,sep) );
                #dprint( event_data[2:].hex() );

                out_event += b'\xFF'
                out_event += b'\x58'
                out_event += event_data[3:];
                #out_event += event_data;



                write_delta( event_delta )
                file.write(out_event);

                

            pass;
        else:
            #Voice Event (regular event)
            event_typeId = ( (first_byte) >> 4);
            

            event_channel : bytes = (first_byte) & 0x0F
            

            if ( event_typeId in midi_event_table ):
                #Valid event that we actually care about (unlike channel pressure for example, who gives a shit about that)
                

                if ( event_typeId == 0x8 ):
                    #Convert 8n event to 9n event with 0 velocity, this is the note off in SEQ apparently
                    

                    out_event += bytes.fromhex( "9" + format(event_channel, "x") );
                    out_event += ( event_data [1 : 2 ] );
                    out_event += ( b'\x00' )

                elif (event_typeId == 0xC and setting["overrideAllPrograms"]["value"] != -1):
                    #Events to skip and not write
                    pass;
                else:
                    #Standard copying the original event as-is
                    out_event = event_data;

                
                if (out_event!= b''):
                    #Remove first byte if running status

                    if ( out_event[0] == running_status and setting["enable_runningStatusWriting"]["value"] ):
                        dprint("should WRITE running status!")
                        out_event = out_event[1:];

                    prev_absolute = event_absolute;
                    
                    write_delta( event_delta );
                    file.write( out_event );

                    running_status = out_event[0];

        if ( out_event != b'' ):
            
            dprint( "src hex:" ,  bytes2hex(event_data) )
            dprint("out:" , bytes2hex(out_event) );
            dprint("")





def start_writing_file():
    print("")
    print_topic("step 4 - writing seq file")

    global track_amount; #python is so f stupid i swear to god
    global song_bpm; 
    global song_timesig;

    #Signature
    file.write( bytes("pQES", 'utf-8' ) );
    #Version (just 1 in this case)
    file.write( b'\x00\x00\x00\x01' );
    #Ticks per quarter note
    file.write( input_tick );


    #Tempo (3 bytes, in microseconds per quarter note)
    

    if (song_bpm == None):
        #Default will be 150
        song_bpm = 150;
    if (song_timesig == [] ):
        song_timesig = [4, 4]

    seconds_per_beat : float = 1/(song_bpm / 60)
    bpm_to_tempo : int = int(seconds_per_beat * 1000000);
    
    file.write ( bpm_to_tempo.to_bytes(3, byteorder='big' ) );

    #Time sig
    timesig_numerator = song_timesig[0];
    timesig_denominator = denominator_to_pow( song_timesig[1] );
    file.write ( timesig_numerator.to_bytes() ); 
    file.write ( timesig_denominator.to_bytes() );



    track_amount = min(track_amount,16);
    empty_list = () * track_amount;

    #Init volumes
    if ( starting_channel_vol != empty_list ):
        for track_number in range(track_amount):
            _start_val = starting_channel_vol[track_number];
            if ( _start_val != None ):
                write_control_change( 0, track_number, 7, _start_val );

    #Init panning
    if ( starting_channel_pan != empty_list ):
        for track_number in range(track_amount):
            _start_val = starting_channel_pan[track_number];
            if ( _start_val != None ):
                write_control_change( 0, track_number, 10, _start_val );

    #Init program change
    for track_number in range(track_amount):
        _start_val = starting_channel_program[track_number];

        if ( setting["overrideAllPrograms"]["value"] != -1  ):
            write_program_change( 0, track_number , setting["overrideAllPrograms"]["value"] );
        elif ( _start_val != None ):
            write_program_change( 0, track_number, _start_val );

        


    pass;





with open(output_path, "wb") as file:
    #Before we write anything

    read_and_list();

    dprint("event list:");
    for _t in event_list:
        for e in _t:
            dprint(e);


    #Step 2

    merge_list();




    start_writing_file();



    #Set loop start
    if (not hasLoopEvent):
        #If MIDI doesnt have loop event, we add a default one at the start of sequence
        write_loop_start();

    main_sequence();

    write_loop_end(0);



input("Finished Writing! Press any key to exit...")
