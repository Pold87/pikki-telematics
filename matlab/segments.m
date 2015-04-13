addpath('~/drivers/3');
tripcount = 200;

segmenters = [ 0 ; 5 ; 40 ; 60 ; 90 ; 130 ; 200];

%%%
% percentages = zeros(size(segmenters,1), tripcount);
% 
% parfor iter = 1 : tripcount
%     trip = csvread([num2str(iter) '.csv'], 1, 0);
%     speeds = sqrt(sum(( trip(1:end-1, :) - trip(2:end, :) ).^2,2));
%     segmentmarkers = zeros(size(speeds,1),1);
% 
%     for iter2 = 1 : size(segmenters)
%         segmentmarkers = segmentmarkers + double(speeds <= segmenters(iter2));
%     end
%     
%     percentages(:,iter) = histc(segmentmarkers, 1:size(segmenters,1)) ./ size(segmentmarkers,1);
% end
%%%        

%%%
trip = csvread([num2str(1) '.csv'], 1, 0);
trip = rotate(trip);  
speeds = sqrt(sum(( trip(1:end-1, :) - trip(2:end, :) ).^2,2));
speeds = speeds * 3.6;  % km/h
minspeed = min(speeds);
maxspeed = max(speeds);
segmentmarkers = zeros(size(speeds,1),1);

for iter = 1 : size(segmenters)
    segmentmarkers = segmentmarkers + double(speeds <= segmenters(iter));
end
figure;
hold on;
% r = 130 - 200
% g = 90  - 130
% b = 60  - 90
% c = 40  - 60
% m = 5   - 40
% y = 0   - 5
% k = 0
colors = 'rgbcmyk';

for iter = 1 : 7
    xs = trip(segmentmarkers == iter, 1);
    ys = trip(segmentmarkers == iter, 2);
    fraction = 1 / max(segmentmarkers) * iter;
    
    plot(xs, ys, ['.' colors(iter)]);
end
%%%
