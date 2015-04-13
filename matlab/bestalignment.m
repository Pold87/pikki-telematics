function [score, alignment ] = bestalignment(trip1, trip2)
    matrix = ...
        [ 5 -10 -5 ; ...
        -10   5 -5; ...
         -5  -5  5];
    gap = 20;
    extendgap = 5;

    [score, alignment]   = nwalign(trip1, trip2, 'Alphabet', 'NT', 'ScoringMatrix', matrix, 'GapOpen', gap, 'EXTENDGAP', extendgap);

    [score2, alignment2] = nwalign(trip1, fliplr(trip2), 'Alphabet', 'NT', 'ScoringMatrix', matrix, 'GapOpen', gap, 'EXTENDGAP', extendgap);
    if score2 > score
        score = score2;
        alignment = alignment2;
    end

    trip2mirrored = strrep(trip2, 'C', 'T');
    trip2mirrored = strrep(trip2mirrored, 'A', 'C');
    trip2mirrored = strrep(trip2mirrored, 'T', 'A');

    [score2, alignment2] = nwalign(trip1, trip2mirrored, 'Alphabet', 'NT', 'ScoringMatrix', matrix, 'GapOpen', gap, 'EXTENDGAP', extendgap);
    if score2 > score
        score = score2;
        alignment = alignment2;
    end

    [score2, alignment2] = nwalign(trip1, fliplr(trip2mirrored), 'Alphabet', 'NT', 'ScoringMatrix', matrix, 'GapOpen', gap, 'EXTENDGAP', extendgap);
    if score2 > score
        score = score2;
        alignment = alignment2;
    end
end

