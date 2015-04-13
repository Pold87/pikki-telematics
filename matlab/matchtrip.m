function [ probs ] = matchtrip( driver, map )

trips = 200;
anglesequences{trips} = [];
tripsequences{trips} = [];

%%% matlabpool to initialize workers
for trip = 1:trips
	tripsequences{trip} = csvread([driver num2str(trip) '.csv'], 1, 0);
	anglesequences{trip} = extractAngles(tripsequences{trip});
end

%% 
% 1
simplified{trips} = [];

anglethreshold = 5; % 5 degrees
distancethreshold = 10; % 10 meters

for trip = 1:trips
	sequence = [];
    angle = 0;
    distance = 0;
    
    for iter = 2 : length(anglesequences{trip}) - 1
        if distance < distancethreshold
            distance = distance + abs(pdist2(tripsequences{trip}(iter-1,:), tripsequences{trip}(iter,:)));
            angle = anglesequences{trip}(iter);
            continue;
        end
        
        if angle > anglethreshold
			sequence = [sequence, 'A'];
        elseif angle < -anglethreshold
            sequence = [sequence, 'C'];
        else
            sequence = [sequence, 'G'];
		
        end
        
        angle = 0;
        distance = 0;
    end
    
	simplified{trip} = sequence;
end


%%
% 2
sym_scores = zeros(trips, trips);
sym_scores(logical(eye(size(sym_scores)))) = -Inf;

for trip1 = 1:trips
    seq1 = simplified{trip1};
	for trip2 = trip1+1:trips
        seq2 = simplified{trip2};
        if isempty(seq1) || isempty(seq2) 
            sym_scores(trip1, trip2) = -Inf;
        else
            [score, ~] = bestalignment(seq1, seq2);
            sym_scores(trip1, trip2) = score;
        end
	end
end

%copy over diagonal
sym_scores = sym_scores + triu(sym_scores, 1)';

%%
% 3

% amount of high similarity scores per trip
counts = sum(sym_scores > 0,2);

probs = zeros(1,trips);

for trip = 1 : trips
    probs(trip) = map(counts(trip)+1);
end

end

