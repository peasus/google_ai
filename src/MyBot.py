#!/usr/bin/env python
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""

from optparse import OptionParser
from PlanetWars import PlanetWars
from datetime import datetime
import pickle


def DoTurn(pw):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(pw.MyFleets()) >= 1:
        return
    # (2) Find my strongest planet.
    source = -1
    source_score = -999999.0
    source_num_ships = 0
    my_planets = pw.MyPlanets()
    for p in my_planets:
        score = float(p.NumShips())
        if score > source_score:
            source_score = score
            source = p.PlanetID()
            source_num_ships = p.NumShips()

    # (3) Find the weakest enemy or neutral planet.
    dest = -1
    dest_score = -999999.0
    not_my_planets = pw.NotMyPlanets()
    for p in not_my_planets:
        score = 1.0 / (1 + p.NumShips())
        if score > dest_score:
            dest_score = score
            dest = p.PlanetID()

    # (4) Send half the ships from my strongest planet to the weakest
    # planet that I do not own.
    if source >= 0 and dest >= 0:
        num_ships = source_num_ships / 2
        pw.IssueOrder(source, dest, num_ships)

log_handle = None
replay_handle = None
replay_version = 1

def main():
    parser = OptionParser()
    parser.add_option("-l", "--log", action="store_true", dest="log", default=False )
    parser.add_option("-o", "--log_file", dest="log_file")
    parser.add_option("-r", "--replay", dest="replay_file" )
    
    (options, args) = parser.parse_args()
    
    # don't want to have logging and replaying... doesn't make sense    
    assert( not (options.log and options.replay_file) )
    
    global log_handle
    if options.log:       
        log_file = "log_" + datetime.now().strftime("%m_%d_%I_%M") + ".rai"
        if options.log_file:
            log_file = options.log_file
        
        log_handle = open(log_file, 'wb' )
    
    if not options.replay_file:
        PlayGame(options.log, log_handle )
    else:
        global replay_handle
        replay_handle = open( options.replay_file, 'rb' )
        ReplayGame(replay_handle)
    
def ReplayGame(replay_handle):
    assert(replay_handle)
    version = int(replay_handle.readline())
    assert(version == replay_version)
    while(True):
        action = replay_handle.readline()
        if action == "continue\n":
            pw = pickle.load(replay_handle)
            DoTurn(pw)
        else:
            break
        

def PlayGame( should_log = False, log_handle = None ):
    if should_log:
        version_string = "%d\n" % (replay_version)
        log_handle.write( version_string )
    map_data = ''
    while(True):
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            if should_log:
                log_handle.write("continue\n")
                pickle.dump(pw, log_handle)
            DoTurn(pw)
            pw.FinishTurn()
            map_data = ''
        else:
            map_data += current_line + '\n'

def cleanup():
    print "cleanup"
    if log_handle:
        log_handle.write("finish\n")
        log_handle.close()
    if replay_handle:
        replay_handle.close()

if __name__ == '__main__':        
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        main()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'
        cleanup()
    except EOFError:
        print 'Replay finished'
        cleanup()
    except:
        print "Unhandled exception..."
        cleanup()
        raise
    else:
        cleanup()
