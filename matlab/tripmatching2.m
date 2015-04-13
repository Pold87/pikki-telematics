folder = '../drivers/1667/';

trips = 200;
anglesequences{trips} = [];
tripsequences{trips} = [];

turns = 50;
freqs = 20;
bins = 10;

% cntr = 1;
%%% matlabpool to initialize workers
parfor trip = 1:trips
	tripsequences{trip} = csvread([folder num2str(trip) '.csv'], 1, 0);
	anglesequences{trip} = extractAngles(tripsequences{trip});
end

% sym_scores = zeros(trips, trips);
% for i = 1:trips
% 	for j = i + 1:trips
% 		sym_scores(i, j) = seqalign(sequences{i}, sequences{j});
% 	end
% end
% sym_scores
% seqalign(sequences{1}, sequences{2})

%% 
1
% trips = 10;
simplified{trips} = [];

nts = [];
anglethreshold = .5;
distancethreshold = 10;

parfor trip = 1:trips
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
2
sym_scores = repmat(0, trips, trips);
sym_scores(logical(eye(size(sym_scores)))) = -Inf;

for trip1 = 1:trips
    seq1 = simplified{trip1};
    [num2str(trip1) ' / ' num2str(trips)]
	parfor trip2 = trip1+1:trips
        seq2 = simplified{trip2};
        if isempty(seq1) || isempty(seq2) 
            sym_scores(trip1, trip2) = -Inf;
        else
            [score, alignment] = bestalignment(seq1, seq2);
            sym_scores(trip1, trip2) = score;
        end
	end
end

%copy over diagonal
sym_scores = sym_scores + triu(sym_scores, 1)';

% for i = 1:trips
% 	for j = i + 1:trips
% 		sym_scores(i, j) = seqalign(sequences{i}, sequences{j});
% 	end
% end
% scores_lower = tril(sym_scores, -1);
% scores_upper = triu(sym_scores,  1);
% sym_scores = scores_lower(:, 1:end - 1) + scores_upper(:, 2:end);

%%
% 3

map = [.5, zeros(1, trips - 1)];
diff = .1;
for iter = 2 : trips - 1
    map(iter) = 1 - diff;
    diff = diff / 2;
end
% amount of high similarity scores per trip
counts = sum(sym_scores > 0,2);

probs = zeros(1,trips);

for trip = 1 : trips
    probs(trip) = map(counts(trip)+1);
end



% sorted = sort(sym_scores, 'descend');
% probs = mean(sorted(1:5, :)) / max(mean(sorted(1:5, :)));
% size( sym_scores(sym_scores > 0))
% % hist(probs, 20)
% % HeatMap(flipdim(sym_scores,1));
% 
for i = 1 : 50
    [val, idx] = max(sym_scores(i,:));
    trip1 = rotate(csvread([folder num2str(i) '.csv'], 1, 0));
    trip2 = rotate(csvread([folder num2str(idx) '.csv'], 1, 0));

    figure;
    hold on
    title(['symscore= ' num2str(val) ' | ' num2str(i) ' and ' num2str(idx)]);
    plot(trip1(:,1), trip1(:,2), '-k');
    plot(trip2(:,1), trip2(:,2), '-r');
    hold off
end
% 
% for i = 1:200; 
%     for j = 1:200; 
%         if sym_scores(i,j) > 50  ; 
%             [num2str(i) ',' num2str(j)]
%             trip1 = rotate(csvread([folder num2str(i) '.csv'], 1, 0));
%             trip2 = rotate(csvread([folder num2str(idx) '.csv'], 1, 0));
% 
%             figure;
%             hold on
%             title(['symscore=' num2str(sym_scores(i,j))]);
%             plot(trip1(:,1), trip1(:,2), '-k');
%             plot(trip2(:,1), trip2(:,2), '-r');
%             hold off
%         end
%     end
% end


